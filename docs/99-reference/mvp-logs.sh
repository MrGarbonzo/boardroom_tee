#!/bin/bash
# mvp-logs.sh - View logs for MVP deployment

CLIENT_ID=${1:-"demo-client"}
COMPONENT=${2:-"all"}

echo "📋 Boardroom TEE MVP Logs - Client: $CLIENT_ID"

case $COMPONENT in
    "hub")
        echo "🏛️ Hub Logs:"
        docker logs -f boardroom-hub-$CLIENT_ID
        ;;
    "finance")
        echo "💰 Finance Agent Logs:"
        docker logs -f finance-agent-$CLIENT_ID
        ;;
    "marketing")
        echo "📈 Marketing Agent Logs:"
        docker logs -f marketing-agent-$CLIENT_ID
        ;;
    "all")
        echo "📋 All Component Logs (last 50 lines each):"
        echo ""
        echo "🏛️ Hub (last 50 lines):"
        docker logs --tail 50 boardroom-hub-$CLIENT_ID
        echo ""
        echo "💰 Finance Agent (last 50 lines):"
        docker logs --tail 50 finance-agent-$CLIENT_ID
        echo ""
        echo "📈 Marketing Agent (last 50 lines):"
        docker logs --tail 50 marketing-agent-$CLIENT_ID
        ;;
    "follow")
        echo "📋 Following all logs (Ctrl+C to stop):"
        docker logs -f boardroom-hub-$CLIENT_ID &
        docker logs -f finance-agent-$CLIENT_ID &
        docker logs -f marketing-agent-$CLIENT_ID &
        wait
        ;;
    *)
        echo "Usage: $0 <client-id> [hub|finance|marketing|all|follow]"
        echo ""
        echo "Examples:"
        echo "  $0 $CLIENT_ID hub      # Hub logs only"
        echo "  $0 $CLIENT_ID finance  # Finance agent logs only"
        echo "  $0 $CLIENT_ID all      # All logs (last 50 lines)"
        echo "  $0 $CLIENT_ID follow   # Follow all logs live"
        ;;
esac
