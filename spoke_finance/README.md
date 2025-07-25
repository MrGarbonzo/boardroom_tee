# Boardroom TEE Finance Agent

## Quick Start
```bash
cd F:/coding/boardroom_tee/spoke_finance
docker-compose up -d
```

## Complete Documentation
**All finance agent implementation details have been moved to the centralized documentation:**

📖 **[Complete Finance Agent Implementation Guide](../docs/02-implementation/finance-agent-implementation.md)**

Includes:
- AdaptLLM/finance-LLM (7B) integration
- Financial analysis and ROI calculations
- Agent collaboration protocols
- Docker configuration and deployment
- Specialization areas and capabilities

## MVP Quick Reference
- **Port**: 8081 (API), 29344 (attestation)
- **Model**: AdaptLLM/finance-LLM (7B parameters) - **Specialized financial model**
- **Resources**: 2 vCPU, 8GB RAM, 40GB storage
- **Purpose**: Financial analysis with Marketing collaboration
- **Key Demo**: Finance-Marketing ROI analysis

## Health Check
```bash
curl http://localhost:8081/health
```

---
*For complete implementation details, see: [`../docs/02-implementation/finance-agent-implementation.md`](../docs/02-implementation/finance-agent-implementation.md)*