#!/bin/bash

# Deploy Boardroom TEE MVP across multiple VMs
# Usage: ./scripts/deploy_mvp.sh [CLIENT_ID] [DEPLOYMENT_MODE]

set -e

CLIENT_ID=${1:-"demo-client"}
DEPLOYMENT_MODE=${2:-"development"}  # development | production
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "🚀 Deploying Boardroom TEE MVP"
echo "Client ID: $CLIENT_ID"
echo "Deployment Mode: $DEPLOYMENT_MODE"
echo ""

# Set environment variables based on deployment mode
if [ "$DEPLOYMENT_MODE" = "production" ]; then
    export DEVELOPMENT_MODE=false
    export MOCK_TEE_ATTESTATION=false
    export MOCK_LLM_PROCESSING=false
    echo "🔒 Production mode: Real TEE and LLM processing"
else
    export DEVELOPMENT_MODE=true
    export MOCK_TEE_ATTESTATION=true
    export MOCK_LLM_PROCESSING=true
    echo "🔧 Development mode: Mocked TEE and LLM processing"
fi

export CLIENT_ID="$CLIENT_ID"

# Create directories for each component
echo "📁 Setting up component directories..."
for component in hub spoke_finance spoke_marketing; do
    cd "$PROJECT_ROOT/$component"
    mkdir -p data logs crypto config
    
    # Copy environment file if it doesn't exist
    if [ ! -f .env ]; then
        cp .env.example .env
        echo "✅ Created .env for $component"
    fi
done

# Deploy Hub (VM 1)
echo ""
echo "📊 Deploying Hub Component..."
cd "$PROJECT_ROOT/hub"

# Generate development crypto keys if needed
if [ "$DEPLOYMENT_MODE" = "development" ] && [ ! -f crypto/privkey.pem ]; then
    echo "🔑 Generating development crypto keys for Hub..."
    mkdir -p crypto
    # In development, we'll let the application generate mock keys
    touch crypto/.gitkeep
fi

docker-compose up -d
echo "✅ Hub deployed on port 8080"

# Wait for Hub to be ready
echo "⏳ Waiting for Hub to be ready..."
for i in {1..30}; do
    if curl -sf http://localhost:8080/health >/dev/null 2>&1; then
        echo "✅ Hub is ready!"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "❌ Hub failed to start after 30 attempts"
        exit 1
    fi
    sleep 2
done

# Deploy Finance Agent (VM 2)
echo ""
echo "💰 Deploying Finance Agent..."
cd "$PROJECT_ROOT/spoke_finance"

# Generate development crypto keys if needed
if [ "$DEPLOYMENT_MODE" = "development" ] && [ ! -f crypto/privkey.pem ]; then
    echo "🔑 Generating development crypto keys for Finance Agent..."
    mkdir -p crypto
    touch crypto/.gitkeep
fi

# Set Hub endpoint
export HUB_ENDPOINT="http://localhost:8080"
export HUB_ATTESTATION_ENDPOINT="http://localhost:29343"

docker-compose up -d
echo "✅ Finance Agent deployed on port 8081"

# Wait for Finance Agent to be ready
echo "⏳ Waiting for Finance Agent to be ready..."
for i in {1..30}; do
    if curl -sf http://localhost:8081/health >/dev/null 2>&1; then
        echo "✅ Finance Agent is ready!"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "❌ Finance Agent failed to start after 30 attempts"
        exit 1
    fi
    sleep 2
done

# Deploy Marketing Agent (VM 3)
echo ""
echo "📈 Deploying Marketing Agent..."
cd "$PROJECT_ROOT/spoke_marketing"

# Generate development crypto keys if needed
if [ "$DEPLOYMENT_MODE" = "development" ] && [ ! -f crypto/privkey.pem ]; then
    echo "🔑 Generating development crypto keys for Marketing Agent..."
    mkdir -p crypto
    touch crypto/.gitkeep
fi

# Set Hub endpoint
export HUB_ENDPOINT="http://localhost:8080"
export HUB_ATTESTATION_ENDPOINT="http://localhost:29343"

docker-compose up -d
echo "✅ Marketing Agent deployed on port 8082"

# Wait for Marketing Agent to be ready
echo "⏳ Waiting for Marketing Agent to be ready..."
for i in {1..30}; do
    if curl -sf http://localhost:8082/health >/dev/null 2>&1; then
        echo "✅ Marketing Agent is ready!"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "❌ Marketing Agent failed to start after 30 attempts"
        exit 1
    fi
    sleep 2
done

# Update Hub with spoke endpoints
echo ""
echo "🔗 Configuring Hub with spoke endpoints..."
cd "$PROJECT_ROOT/hub"

# Update .env with spoke endpoints
if grep -q "FINANCE_ENDPOINT=" .env; then
    sed -i 's|FINANCE_ENDPOINT=.*|FINANCE_ENDPOINT=http://localhost:8081|' .env
else
    echo "FINANCE_ENDPOINT=http://localhost:8081" >> .env
fi

if grep -q "MARKETING_ENDPOINT=" .env; then
    sed -i 's|MARKETING_ENDPOINT=.*|MARKETING_ENDPOINT=http://localhost:8082|' .env
else
    echo "MARKETING_ENDPOINT=http://localhost:8082" >> .env
fi

# Restart Hub to pick up new endpoints
docker-compose restart
echo "✅ Hub restarted with spoke endpoints"

# Final health check
echo ""
echo "🏥 Final Health Check..."
sleep 5

HEALTH_CHECKS=(
    "Hub:http://localhost:8080/health"
    "Finance:http://localhost:8081/health"
    "Marketing:http://localhost:8082/health"
)

for check in "${HEALTH_CHECKS[@]}"; do
    IFS=':' read -r name url <<< "$check"
    if curl -sf "$url" >/dev/null 2>&1; then
        echo "✅ $name is healthy"
    else
        echo "❌ $name is not responding"
    fi
done

echo ""
echo "🎉 Deployment Complete!"
echo ""
echo "📋 Service Endpoints:"
echo "  Hub:       http://localhost:8080"
echo "  Finance:   http://localhost:8081"
echo "  Marketing: http://localhost:8082"
echo ""
echo "🔍 Attestation Endpoints:"
echo "  Hub:       http://localhost:29343/attestation"
echo "  Finance:   http://localhost:29344/attestation"
echo "  Marketing: http://localhost:29345/attestation"
echo ""
echo "🧪 Test the deployment:"
echo "  ./scripts/test_deployment.sh"
echo ""
echo "📊 View logs:"
echo "  docker-compose logs -f  # (run in component directory)"