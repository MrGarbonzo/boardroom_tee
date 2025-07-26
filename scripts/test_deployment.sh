#!/bin/bash

# Test Boardroom TEE MVP deployment
# Usage: ./scripts/test_deployment.sh [CLIENT_ID]

set -e

CLIENT_ID=${1:-"demo-client"}

echo "🧪 Testing Boardroom TEE MVP Deployment"
echo "Client ID: $CLIENT_ID"
echo ""

# Test endpoints
ENDPOINTS=(
    "Hub Health:http://localhost:8080/health"
    "Finance Health:http://localhost:8081/health"
    "Marketing Health:http://localhost:8082/health"
    "Hub Attestation:http://localhost:29343/attestation"
    "Finance Attestation:http://localhost:29344/attestation"
    "Marketing Attestation:http://localhost:29345/attestation"
)

echo "🔍 Testing Basic Endpoints..."
for endpoint in "${ENDPOINTS[@]}"; do
    IFS=':' read -r name url <<< "$endpoint"
    echo -n "  Testing $name... "
    
    if response=$(curl -sf "$url" 2>/dev/null); then
        echo "✅ OK"
    else
        echo "❌ FAILED"
        echo "    URL: $url"
    fi
done

echo ""
echo "🤖 Testing Agent Capabilities..."

# Test Hub document upload
echo -n "  Hub document upload... "
if curl -sf -X POST "http://localhost:8080/api/v1/documents/upload" \
    -H "X-Client-ID: $CLIENT_ID" \
    -F "file=@/dev/null" \
    -F "department=finance" \
    >/dev/null 2>&1; then
    echo "✅ OK"
else
    echo "❌ FAILED (expected - no real file)"
fi

# Test Finance Agent capabilities
echo -n "  Finance Agent capabilities... "
if response=$(curl -sf "http://localhost:8081/api/v1/capabilities" 2>/dev/null); then
    if echo "$response" | grep -q "financial_analysis"; then
        echo "✅ OK"
    else
        echo "❌ FAILED (missing capabilities)"
    fi
else
    echo "❌ FAILED"
fi

# Test Marketing Agent capabilities
echo -n "  Marketing Agent capabilities... "
if response=$(curl -sf "http://localhost:8082/api/v1/capabilities" 2>/dev/null); then
    if echo "$response" | grep -q "marketing_analysis"; then
        echo "✅ OK"
    else
        echo "❌ FAILED (missing capabilities)"
    fi
else
    echo "❌ FAILED"
fi

echo ""
echo "💬 Testing Agent Collaboration..."

# Test Marketing ROI Analysis
echo -n "  Marketing ROI analysis... "
roi_request='{
    "campaign_name": "Holiday Campaign",
    "marketing_spend": 50000,
    "impressions": 1000000,
    "clicks": 25000,
    "conversions": 500
}'

if response=$(curl -sf -X POST "http://localhost:8082/api/v1/campaign/analyze" \
    -H "Content-Type: application/json" \
    -d "$roi_request" 2>/dev/null); then
    if echo "$response" | grep -q "analysis_type"; then
        echo "✅ OK"
    else
        echo "❌ FAILED (invalid response)"
    fi
else
    echo "❌ FAILED"
fi

# Test Finance ROI Calculation
echo -n "  Finance ROI calculation... "
finance_request='{
    "investment_data": {"total_investment": 50000, "time_period_months": 3},
    "revenue_data": {"total_returns": 75000}
}'

if response=$(curl -sf -X POST "http://localhost:8081/api/v1/process" \
    -H "Content-Type: application/json" \
    -d '{"type": "roi_analysis", "context": '"$finance_request"'}' 2>/dev/null); then
    if echo "$response" | grep -q "analysis_type"; then
        echo "✅ OK"
    else
        echo "❌ FAILED (invalid response)"
    fi
else
    echo "❌ FAILED"
fi

echo ""
echo "🔐 Testing Security Features..."

# Test attestation endpoints
echo -n "  Hub attestation verification... "
if response=$(curl -sf "http://localhost:29343/attestation" 2>/dev/null); then
    if echo "$response" | grep -q "status"; then
        echo "✅ OK"
    else
        echo "❌ FAILED (invalid attestation)"
    fi
else
    echo "❌ FAILED"
fi

echo -n "  Agent attestation verification... "
if response=$(curl -sf "http://localhost:29344/attestation" 2>/dev/null); then
    if echo "$response" | grep -q "status"; then
        echo "✅ OK"
    else
        echo "❌ FAILED (invalid attestation)"
    fi
else
    echo "❌ FAILED"
fi

echo ""
echo "📊 Component Status Summary:"

# Get detailed status
for port in 8080 8081 8082; do
    service_name=""
    case $port in
        8080) service_name="Hub" ;;
        8081) service_name="Finance Agent" ;;
        8082) service_name="Marketing Agent" ;;
    esac
    
    echo "  $service_name (port $port):"
    if response=$(curl -sf "http://localhost:$port/health" 2>/dev/null); then
        status=$(echo "$response" | grep -o '"status":"[^"]*"' | cut -d'"' -f4)
        development_mode=$(echo "$response" | grep -o '"development_mode":[^,}]*' | cut -d':' -f2)
        echo "    Status: $status"
        echo "    Development Mode: $development_mode"
    else
        echo "    Status: UNREACHABLE"
    fi
done

echo ""
echo "🎯 End-to-End Collaboration Test:"
echo "Try this example workflow:"
echo ""
echo "1. Upload a document:"
echo "   curl -X POST http://localhost:8080/api/v1/documents/upload \\"
echo "     -H 'X-Client-ID: $CLIENT_ID' \\"
echo "     -F 'file=@your-document.pdf' \\"
echo "     -F 'department=marketing'"
echo ""
echo "2. Request ROI analysis:"
echo "   curl -X POST http://localhost:8080/api/v1/orchestration/route \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -H 'X-Client-ID: $CLIENT_ID' \\"
echo "     -d '{\"query\": \"What was the ROI on our holiday marketing campaign?\"}'"
echo ""
echo "🔍 Monitor with:"
echo "   docker-compose logs -f  # (in component directories)"
echo ""
echo "✅ Testing complete!"