# Boardroom TEE Marketing Agent

## Quick Start
```bash
cd F:/coding/boardroom_tee/spoke_marketing
docker-compose up -d
```

## Complete Documentation
**All marketing agent implementation details have been moved to the centralized documentation:**

📖 **[Complete Marketing Agent Implementation Guide](../docs/02-implementation/marketing-agent-implementation.md)**

Includes:
- Mistral-7B-Instruct-v0.3 (7B) integration
- Campaign analysis and customer intelligence
- Agent collaboration protocols
- Docker configuration and deployment
- Specialization areas and capabilities

## MVP Quick Reference
- **Port**: 8082 (API), 29345 (attestation)
- **Model**: mistralai/Mistral-7B-Instruct-v0.3 (7B parameters) - **General-purpose 7B model**
- **Resources**: 2 vCPU, 8GB RAM, 20GB storage
- **Purpose**: Marketing intelligence with Finance collaboration
- **Key Demo**: Campaign analysis for Finance ROI calculation

## Health Check
```bash
curl http://localhost:8082/health
```

---
*For complete implementation details, see: [`../docs/02-implementation/marketing-agent-implementation.md`](../docs/02-implementation/marketing-agent-implementation.md)*