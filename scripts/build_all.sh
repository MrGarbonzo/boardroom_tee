#!/bin/bash

# Build all Boardroom TEE components
# Usage: ./scripts/build_all.sh [CLIENT_ID]

set -e

CLIENT_ID=${1:-"demo-client"}
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "🚀 Building Boardroom TEE MVP - All Components"
echo "Client ID: $CLIENT_ID"
echo "Project Root: $PROJECT_ROOT"

# Build Hub
echo ""
echo "📊 Building Hub Component..."
cd "$PROJECT_ROOT/hub"
docker build -t boardroom-tee-hub:latest .
docker tag boardroom-tee-hub:latest ghcr.io/your-org/boardroom-tee-hub:latest

# Build Finance Agent
echo ""
echo "💰 Building Finance Agent..."
cd "$PROJECT_ROOT/spoke_finance"
docker build -t boardroom-tee-finance:latest .
docker tag boardroom-tee-finance:latest ghcr.io/your-org/boardroom-tee-finance:latest

# Build Marketing Agent
echo ""
echo "📈 Building Marketing Agent..."
cd "$PROJECT_ROOT/spoke_marketing"
docker build -t boardroom-tee-marketing:latest .
docker tag boardroom-tee-marketing:latest ghcr.io/your-org/boardroom-tee-marketing:latest

echo ""
echo "✅ All components built successfully!"
echo ""
echo "📋 Available Images:"
docker images | grep boardroom-tee

echo ""
echo "🎯 Next Steps:"
echo "1. Configure .env files in each component directory"
echo "2. Run: ./scripts/deploy_mvp.sh $CLIENT_ID"
echo "3. Test endpoints with: ./scripts/test_deployment.sh"