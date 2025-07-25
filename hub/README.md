# Boardroom TEE Hub

## MVP Quick Start
```bash
# Deploy complete MVP (Hub + Finance + Marketing)
./docs/99-reference/mvp-deploy.sh demo-client

# Or deploy hub only
cd F:/coding/boardroom_tee/hub
docker-compose up -d
```

## Complete Documentation
**All hub implementation details have been moved to the centralized documentation:**

📖 **[Complete Hub Implementation Guide](../docs/02-implementation/hub-implementation.md)**

Includes:
- Unified LLM architecture (Llama-3.2-1B-Instruct)
- Document processing pipeline
- Agent orchestration and registry
- Attestation discovery service
- Docker configuration and deployment
- API endpoint implementations

## Quick Reference
- **Port**: 8080 (API), 29343 (attestation)
- **Model**: meta-llama/Llama-3.2-1B-Instruct
- **Resources**: 2 vCPU, 4GB RAM, TB+ storage
- **Purpose**: Data organization + agent orchestration

## Health Check
```bash
curl http://localhost:8080/health
```

---
*For complete implementation details, see: [`../docs/02-implementation/hub-implementation.md`](../docs/02-implementation/hub-implementation.md)*