# Claude Code Generation Reference - Boardroom TEE

## Quick Navigation for Implementation

### 🏗️ MVP Implementation (Phase 1)
- **Hub Implementation**: [`02-implementation/hub-implementation.md`](./02-implementation/hub-implementation.md)
- **Finance Agent**: [`02-implementation/finance-agent-implementation.md`](./02-implementation/finance-agent-implementation.md)
- **Marketing Agent**: [`02-implementation/marketing-agent-implementation.md`](./02-implementation/marketing-agent-implementation.md)

### 🚀 Future Phases
- **Sales Agent**: Phase 2 expansion
- **CEO Agent**: Phase 3 with SecretAI integration

### 🚀 Deployment Options
- **Docker Deployment**: [`03-deployment/docker-deployment.md`](./03-deployment/docker-deployment.md)
- **dstack TEE Platform**: [`03-deployment/dstack-deployment.md`](./03-deployment/dstack-deployment.md)

### 🔌 API Integration
- **Complete API Specs**: [`04-apis/api-specifications.md`](./04-apis/api-specifications.md)
- **Agent Communication**: [`04-apis/agent-protocols.md`](./04-apis/agent-protocols.md)

---

## System Architecture Overview

### Core Innovation: Agent-to-Agent Collaboration
Dynamic multi-specialist analysis without fixed pipeline overhead. Agents collaborate on-demand through secure attestation-verified communication.

### Component Relationships
```
Hub (Llama-3.2-1B) → Data Organization + Agent Orchestration
    ↓ Secure Communication
Spoke Agents → Specialized Analysis + Collaboration
    ↓ Multi-hop Attestation  
Results → Collaborative Intelligence
```

### MVP Technology Stack (Phase 1)
- **Hub**: Llama-3.2-1B-Instruct for data organization + orchestration
- **Finance Agent**: AdaptLLM/Finance-LLM-7B (specialized financial model)
- **Marketing Agent**: Mistral-7B-Instruct-v0.3 (general-purpose 7B model)
- **Security**: SecretVM TEE with verifiable message signing
- **Communication**: Attestation-verified agent-to-agent protocols

### Future Phase Models
- **Sales Agent**: Mistral-7B-Instruct-v0.3 (Phase 2)
- **CEO Agent**: deepseek-ai/deepseek-llm-7b-chat with SecretAI integration (Phase 3)

---

## Component Dependencies

### Hub Dependencies
- **Base Requirements**: Python 3.11, Transformers, FastAPI
- **LLM Model**: meta-llama/Llama-3.2-1B-Instruct (3GB memory)
- **Storage**: Expandable TB+ storage for client data
- **Networking**: Port 8080 (API), 29343 (attestation)
- **Security**: SecretVM TEE, verifiable message signing

### Agent Dependencies
- **Shared Base**: All agents inherit from base agent framework
- **Individual Models**: Each agent loads specialized LLM
- **Hub Communication**: Must register with hub and maintain attestation
- **Inter-Agent**: Direct attestation-verified communication capability

### Deployment Dependencies
- **TEE Environment**: SecretVM or dstack platform
- **Container Runtime**: Docker with TEE integration
- **Networking**: Secure internal communication + external API access
- **Storage**: Persistent volumes for data, logs, crypto keys

---

## Implementation Sequence

### MVP Phase 1: Core Foundation (Build First)
1. **Hub Implementation** → Data ingestion + Llama-3.2-1B processing
2. **Base Agent Framework** → Shared code for all agents
3. **Finance Agent** → AdaptLLM specialized financial analysis
4. **Marketing Agent** → Mistral-7B marketing intelligence
5. **Agent-to-Agent Collaboration** → Finance ↔ Marketing communication
6. **Campaign ROI Analysis** → Key collaboration use case

### Phase 2: Expansion (Future)
1. **Sales Agent** → Pipeline forecasting and lead optimization
2. **Enhanced Collaboration** → 3-way agent workflows
3. **Web Interface** → Frontend for user interaction

### Phase 3: Premium Features (Future)
1. **CEO Agent** → Strategic synthesis with SecretAI integration
2. **Advanced Analytics** → Cross-departmental insights
3. **Enterprise Features** → Monitoring, compliance, optimization

---

## Latest Architecture Decisions

### Agent Collaboration Over Fixed Pipeline
**Decision**: Implement dynamic agent-to-agent collaboration instead of fixed 6-stage pipeline
**Rationale**: More flexible, cost-efficient, and scalable than rigid processing stages
**Impact**: Agents request help from each other through hub-brokered secure communication

### Unified LLM for Hub
**Decision**: Use Llama-3.2-1B-Instruct for both data organization AND agent orchestration
**Rationale**: Single model reduces complexity while handling both text processing and routing decisions
**Impact**: Simpler architecture, lower resource requirements, easier maintenance

### Push-Based Data Model
**Decision**: Companies upload data to us rather than pulling from their systems
**Rationale**: Better security, clearer liability, easier sales process
**Impact**: Need robust upload handling and storage management

### TEE-First Security
**Decision**: All components run in TEE with verifiable message signing
**Rationale**: Hardware-guaranteed security for sensitive business data
**Impact**: Higher infrastructure requirements but unmatched security guarantees

---

## Code Templates & Examples

### Docker Compose Examples
- **Hub Deployment**: [`03-deployment/docker-deployment.md#hub-compose`](./03-deployment/docker-deployment.md#hub-compose)
- **Agent Deployment**: [`03-deployment/docker-deployment.md#agent-compose`](./03-deployment/docker-deployment.md#agent-compose)

### API Endpoint Templates
- **Agent Registration**: [`04-apis/api-specifications.md#agent-register`](./04-apis/api-specifications.md#agent-register)
- **Document Upload**: [`04-apis/api-specifications.md#document-upload`](./04-apis/api-specifications.md#document-upload)
- **Agent Collaboration**: [`04-apis/agent-protocols.md#collaboration-request`](./04-apis/agent-protocols.md#collaboration-request)

### Attestation Integration
- **TEE Key Generation**: [`05-security/attestation-implementation.md#key-generation`](./05-security/attestation-implementation.md#key-generation)
- **Agent Verification**: [`05-security/attestation-implementation.md#agent-verification`](./05-security/attestation-implementation.md#agent-verification)

---

## Configuration Quick Reference

### MVP Environment Variables
```bash
# Hub Configuration
HUB_MODEL_NAME=meta-llama/Llama-3.2-1B-Instruct
HUB_MAX_MEMORY_MB=3000
HUB_API_PORT=8080
HUB_ATTESTATION_PORT=29343

# Finance Agent (Specialized Financial Model)
AGENT_TYPE=finance
AGENT_MODEL_NAME=AdaptLLM/finance-LLM
AGENT_API_PORT=8081
AGENT_ATTESTATION_PORT=29344

# Marketing Agent (General 7B Model)
AGENT_TYPE=marketing
AGENT_MODEL_NAME=mistralai/Mistral-7B-Instruct-v0.3
AGENT_API_PORT=8082
AGENT_ATTESTATION_PORT=29345
```

### MVP Port Allocation
- **Hub**: 8080 (API), 29343 (attestation)
- **Finance**: 8081 (API), 29344 (attestation)
- **Marketing**: 8082 (API), 29345 (attestation)

### Future Phase Ports
- **Sales**: 8083 (API), 29346 (attestation)
- **CEO**: 8084 (API), 29347 (attestation)

### MVP Resource Requirements (Phase 1)
- **Hub**: 2 vCPU, 4GB RAM, TB+ storage
- **Finance Agent**: 2 vCPU, 8GB RAM, 40GB storage (7B model)
- **Marketing Agent**: 2 vCPU, 8GB RAM, 20GB storage (7B model)
- **Total MVP**: 6 vCPU, 20GB RAM, 1TB+ storage

### Future Phase Resources
- **Sales Agent**: 2 vCPU, 8GB RAM, 20GB storage
- **CEO Agent**: 4 vCPU, 12GB RAM, 80GB storage (with SecretAI)

---

## Security Model Summary

### Trust Boundaries
- **Trusted**: TEE hardware, verified agents, encrypted data
- **Untrusted**: Host OS, network, unverified agents
- **Verification**: Hardware attestation + cryptographic proof

### Key Management
- **Generation**: Keys generated within TEE, never exported
- **Distribution**: Public keys shared via attestation quotes
- **Communication**: All messages signed with TEE-generated private keys
- **Rotation**: Automatic re-attestation every 4-6 hours

### Data Protection
- **At Rest**: Encrypted within TEE
- **In Transit**: Encrypted with agent public keys
- **In Processing**: Never leaves TEE boundaries
- **Access Control**: Attestation-based authorization

---

*Last Updated: December 2024*  
*Document Owner: Boardroom TEE Development Team*  
*Purpose: Claude AI code generation reference*