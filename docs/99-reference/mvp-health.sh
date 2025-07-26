#!/bin/bash
# mvp-health.sh - Check health of MVP multi-VM deployment

CLIENT_ID=${1:-"demo-client"}
HUB_IP=${2:-"localhost"}
FINANCE_IP=${3:-"localhost"}
MARKETING_IP=${4:-"localhost"}

echo "🏥 Boardroom TEE MVP Multi-VM Health Check - Client: $CLIENT_ID"
echo "Hub: $HUB_IP | Finance: $FINANCE_IP | Marketing: $MARKETING_IP"
echo "==============================================="

# Hub VM health
echo "🏛️ Hub VM Status ($HUB_IP):"
if curl -s -f http://$HUB_IP:8080/health >/dev/null; then
    curl -s http://$HUB_IP:8080/health | jq '{status: .status, model_loaded: .model_loaded, registered_agents: .registered_agents, memory_usage: .memory_usage}'
    echo "✅ Hub VM: HEALTHY"
else
    echo "❌ Hub VM: UNHEALTHY or unreachable"
fi
echo ""

# Finance VM health
echo "💰 Finance VM Status ($FINANCE_IP):"
if curl -s -f http://$FINANCE_IP:8081/health >/dev/null; then
    curl -s http://$FINANCE_IP:8081/health | jq '{status: .status, agent_type: .agent_type, model_loaded: .model_loaded, attestation_verified: .attestation_verified}'
    echo "✅ Finance VM: HEALTHY"
else
    echo "❌ Finance VM: UNHEALTHY or unreachable"
fi
echo ""

# Marketing VM health
echo "📈 Marketing VM Status ($MARKETING_IP):"
if curl -s -f http://$MARKETING_IP:8082/health >/dev/null; then
    curl -s http://$MARKETING_IP:8082/health | jq '{status: .status, agent_type: .agent_type, model_loaded: .model_loaded, attestation_verified: .attestation_verified}'
    echo "✅ Marketing VM: HEALTHY"
else
    echo "❌ Marketing VM: UNHEALTHY or unreachable"
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

# Cross-VM Communication Test
echo "🤝 Cross-VM Communication Status:"
echo "Checking agent registry from Hub VM..."
curl -s http://$HUB_IP:8080/api/v1/discovery/agents | jq '.verified_agents[] | {agent_id: .agent_id, agent_type: .agent_type, status: .status}' 2>/dev/null || echo "❌ Agent registry check failed - cross-VM communication issue"

echo ""
echo "💡 Multi-VM Next Steps:"
echo "  - All VMs healthy: Ready for cross-VM testing"
echo "  - Any issues: Check logs on individual VMs"
echo "  - Test cross-VM collaboration: Finance + Marketing ROI analysis"
echo "  - Network issues: Verify VM firewall rules and IP connectivity"
