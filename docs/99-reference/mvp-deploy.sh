#!/bin/bash
# mvp-deploy.sh - Deploy Boardroom TEE MVP (Hub + Finance + Marketing)

set -e

CLIENT_ID=${1:-"demo-client"}
echo "🚀 Deploying Boardroom TEE MVP for client: $CLIENT_ID"
echo "Components: Hub + Finance Agent + Marketing Agent"

# Validate environment
if [ -z "$CLIENT_ID" ]; then
    echo "❌ Error: CLIENT_ID required"
    echo "Usage: ./mvp-deploy.sh <client-id>"
    exit 1
fi

# Set environment
export CLIENT_ID=$CLIENT_ID
export HUB_ENDPOINT="https://hub-${CLIENT_ID}.boardroom-tee.com:8080"
export HUB_ATTESTATION_ENDPOINT="https://hub-${CLIENT_ID}.boardroom-tee.com:29343"

echo "📋 MVP Configuration:"
echo "  - Hub: Llama-3.2-1B-Instruct (4GB RAM)"
echo "  - Finance: AdaptLLM/finance-LLM 7B (8GB RAM)"
echo "  - Marketing: Mistral-7B-Instruct-v0.3 (8GB RAM)"
echo "  - Total Resources: 6 vCPU, 20GB RAM"
echo ""

# Create network
echo "🌐 Creating Docker network..."
docker network create boardroom-network --driver bridge 2>/dev/null || echo "Network already exists"

# Deploy Hub (must be first)
echo "🏛️ Deploying Hub..."
cd hub
docker-compose up -d
echo "⏳ Waiting for hub to start..."
sleep 30

# Verify hub health
echo "🔍 Checking hub health..."
for i in {1..5}; do
    if curl -f http://localhost:8080/health >/dev/null 2>&1; then
        echo "✅ Hub is healthy"
        break
    else
        echo "⏳ Hub starting... (attempt $i/5)"
        sleep 10
    fi
done

cd ..

# Deploy Finance Agent
echo "💰 Deploying Finance Agent (AdaptLLM 7B)..."
cd spoke_finance
docker-compose up -d
echo "⏳ Waiting for finance agent to start..."
sleep 45  # 7B model takes longer to load

# Verify finance agent health
echo "🔍 Checking finance agent health..."
for i in {1..5}; do
    if curl -f http://localhost:8081/health >/dev/null 2>&1; then
        echo "✅ Finance Agent is healthy"
        break
    else
        echo "⏳ Finance Agent starting... (attempt $i/5)"
        sleep 15
    fi
done

cd ..

# Deploy Marketing Agent
echo "📈 Deploying Marketing Agent (Mistral 7B)..."
cd spoke_marketing
docker-compose up -d
echo "⏳ Waiting for marketing agent to start..."
sleep 45  # 7B model takes longer to load

# Verify marketing agent health
echo "🔍 Checking marketing agent health..."
for i in {1..5}; do
    if curl -f http://localhost:8082/health >/dev/null 2>&1; then
        echo "✅ Marketing Agent is healthy"
        break
    else
        echo "⏳ Marketing Agent starting... (attempt $i/5)"
        sleep 15
    fi
done

cd ..

# Test agent collaboration
echo "🤝 Testing Finance-Marketing collaboration..."
sleep 10  # Allow agents to register with hub

# Check agent registry
echo "📋 Checking agent registry..."
curl -s http://localhost:8080/api/v1/discovery/agents | jq . || echo "Agent registry check failed"

# Test collaboration routing
echo "🔄 Testing collaboration routing..."
curl -s -X POST http://localhost:8080/api/v1/orchestration/route \
  -H "Content-Type: application/json" \
  -d '{"query": "Test Finance-Marketing collaboration", "requesting_agent": "finance-agent-'$CLIENT_ID'"}' \
  | jq . || echo "Collaboration test failed"

echo ""
echo "🎉 MVP Deployment Complete!"
echo ""
echo "📊 Service Status:"
echo "  Hub:       http://localhost:8080/health"
echo "  Finance:   http://localhost:8081/health"
echo "  Marketing: http://localhost:8082/health"
echo ""
echo "💡 MVP Demo Workflow:"
echo "  1. Upload marketing campaign data to Hub"
echo "  2. Ask: 'What's the ROI on our Q4 holiday campaign?'"
echo "  3. Marketing Agent analyzes campaign performance"
echo "  4. Finance Agent calculates ROI with marketing context"
echo "  5. Hub synthesizes complete financial analysis"
echo ""
echo "🔧 Management Commands:"
echo "  Health:    ./mvp-health.sh $CLIENT_ID"
echo "  Logs:      ./mvp-logs.sh $CLIENT_ID"
echo "  Stop:      ./mvp-stop.sh $CLIENT_ID"
echo ""
echo "📈 Ready for Finance-Marketing collaboration testing!"
