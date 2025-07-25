#!/bin/bash
# mvp-health.sh - Check health of MVP deployment

CLIENT_ID=${1:-"demo-client"}

echo "🏥 Boardroom TEE MVP Health Check - Client: $CLIENT_ID"
echo "================================================"

# Hub health
echo "🏛️ Hub Status:"
if curl -s -f http://localhost:8080/health >/dev/null; then
    curl -s http://localhost:8080/health | jq '{status: .status, model_loaded: .model_loaded, registered_agents: .registered_agents, memory_usage: .memory_usage}'
    echo "✅ Hub: HEALTHY"
else
    echo "❌ Hub: UNHEALTHY"
fi
echo ""

# Finance Agent health
echo "💰 Finance Agent Status:"
if curl -s -f http://localhost:8081/health >/dev/null; then
    curl -s http://localhost:8081/health | jq '{status: .status, agent_type: .agent_type, model_loaded: .model_loaded, attestation_verified: .attestation_verified}'
    echo "✅ Finance Agent: HEALTHY"
else
    echo "❌ Finance Agent: UNHEALTHY"
fi
echo ""

# Marketing Agent health
echo "📈 Marketing Agent Status:"
if curl -s -f http://localhost:8082/health >/dev/null; then
    curl -s http://localhost:8082/health | jq '{status: .status, agent_type: .agent_type, model_loaded: .model_loaded, attestation_verified: .attestation_verified}'
    echo "✅ Marketing Agent: HEALTHY"
else
    echo "❌ Marketing Agent: UNHEALTHY"
fi
echo ""

# Container status
echo "🐳 Container Status:"
docker ps --filter name="$CLIENT_ID" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -E "(boardroom-hub|finance-agent|marketing-agent)"
echo ""

# Resource usage
echo "📊 Resource Usage:"
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}" | grep -E "(boardroom-hub|finance-agent|marketing-agent)"
echo ""

# Agent collaboration status
echo "🤝 Collaboration Status:"
echo "Checking agent registry..."
curl -s http://localhost:8080/api/v1/discovery/agents | jq '.verified_agents[] | {agent_id: .agent_id, agent_type: .agent_type, status: .status}' 2>/dev/null || echo "❌ Agent registry check failed"

echo ""
echo "💡 Next Steps:"
echo "  - All services healthy: Ready for testing"
echo "  - Any issues: Check logs with ./mvp-logs.sh $CLIENT_ID"
echo "  - Test collaboration: See MVP demo workflow"
