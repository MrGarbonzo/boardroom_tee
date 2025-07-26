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
- **Standalone VM Deployment**: [`03-deployment/docker-deployment.md`](./03-deployment/docker-deployment.md)
- **Multi-VM TEE Platform**: [`03-deployment/dstack-deployment.md`](./03-deployment/dstack-deployment.md)

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

### MVP Technology Stack (Phase 1) - Distributed Architecture
- **Hub VM**: Llama-3.2-1B-Instruct for data organization + orchestration
- **Finance VM**: AdaptLLM/Finance-LLM-7B (specialized financial model)
- **Marketing VM**: Mistral-7B-Instruct-v0.3 (general-purpose 7B model)
- **Security**: Cross-VM TEE with Verifiable Message Signing (VMS)
- **Communication**: Direct spoke-to-spoke with hub coordination via VMS-signed messages
- **Message Verification**: Every message cryptographically signed for verifiable AI provenance
- **Deployment**: Each component = separate VM + separate GHCR image

### Future Phase Models
- **Sales Agent**: Mistral-7B-Instruct-v0.3 (Phase 2)
- **CEO Agent**: deepseek-ai/deepseek-llm-7b-chat with SecretAI integration (Phase 3)

---

## Component Dependencies

### Hub VM Dependencies
- **VM Requirements**: 2 vCPU, 4GB RAM, 50GB storage
- **Base Requirements**: Python 3.11, Transformers, FastAPI
- **LLM Model**: meta-llama/Llama-3.2-1B-Instruct (3GB memory)
- **Networking**: Port 8080 (API), 29343 (attestation)
- **GHCR Image**: `ghcr.io/[org]/boardroom-tee-hub:latest`
- **Security**: TEE isolation, cross-VM attestation

### Spoke VM Dependencies
- **VM Requirements**: 2 vCPU, 8GB RAM, 40GB storage each
- **Standalone Apps**: Each spoke is completely self-contained
- **Individual Models**: Each loads specialized LLM (Finance: AdaptLLM/7B, Marketing: Mistral/7B)
- **Hub Communication**: Connects to hub via IP configuration in .env file
- **GHCR Images**: 
  - Finance: `ghcr.io/[org]/boardroom-tee-finance:latest`
  - Marketing: `ghcr.io/[org]/boardroom-tee-marketing:latest`

### Multi-VM Deployment Dependencies
- **TEE Environment**: Each VM runs SecretVM with full attestation verification
- **Container Runtime**: Docker with SecretVM TEE integration on each VM
- **Networking**: Cross-VM communication via public IP addresses
- **Storage**: Persistent volumes per VM for data, logs, crypto keys
- **Configuration**: Manual IP configuration via .env files
- **VMS Keys**: Automatic ed25519 key generation per VM via SecretVM volume mounts
- **Key Rotation**: Weekly key rotation with graceful transition
- **Message Signing**: Every cross-VM message cryptographically signed
- **Client Isolation**: Dedicated VM set (hub + spokes) per business client
- **Independent Verification**: Clients can verify TEE integrity via port 29343 attestation endpoint

---

## Implementation Sequence - Standalone VM Architecture

### MVP Phase 1: Distributed Foundation (Build First)
1. **Hub VM Application** → Standalone data ingestion + Llama-3.2-1B processing
2. **Finance VM Application** → Standalone AdaptLLM specialized financial analysis
3. **Marketing VM Application** → Standalone Mistral-7B marketing intelligence
### 4. **Cross-VM Communication** → Dedicated VM sets with auto-discovery per business client
5. **Hub Coordination** → Spoke directory and attestation verification
6. **Client Isolation** → Complete VM-level separation per business (no shared infrastructure)
7. **Campaign ROI Analysis** → Multi-VM collaboration use case with signed responses

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

### MVP Environment Variables - Per VM Configuration

**Hub VM (.env):**
```bash
HUB_MODEL_NAME=meta-llama/Llama-3.2-1B-Instruct
HUB_MAX_MEMORY_MB=3000
HUB_API_PORT=8080
HUB_ATTESTATION_PORT=29343
CLIENT_ID=your-company
# Spoke endpoints (configured after spoke deployment)
FINANCE_ENDPOINT=http://[FINANCE_IP]:8081
MARKETING_ENDPOINT=http://[MARKETING_IP]:8082
```

**Finance VM (.env):**
```bash
AGENT_TYPE=finance
AGENT_MODEL_NAME=AdaptLLM/finance-LLM
AGENT_API_PORT=8081
AGENT_ATTESTATION_PORT=29344
CLIENT_ID=your-company
# Hub endpoint (configured during deployment)
HUB_ENDPOINT=http://[HUB_IP]:8080
```

**Marketing VM (.env):**
```bash
AGENT_TYPE=marketing
AGENT_MODEL_NAME=mistralai/Mistral-7B-Instruct-v0.3
AGENT_API_PORT=8082
AGENT_ATTESTATION_PORT=29345
CLIENT_ID=your-company
# Hub endpoint (configured during deployment)
HUB_ENDPOINT=http://[HUB_IP]:8080
```

### MVP Port Allocation
- **Hub**: 8080 (API), 29343 (attestation)
- **Finance**: 8081 (API), 29344 (attestation)
- **Marketing**: 8082 (API), 29345 (attestation)

### Future Phase Ports
- **Sales**: 8083 (API), 29346 (attestation)
- **CEO**: 8084 (API), 29347 (attestation)

### MVP Resource Requirements (Phase 1) - Per Client Deployment
- **Hub VM**: 2 vCPU, 4GB RAM, 50GB storage
- **Finance VM**: 2 vCPU, 8GB RAM, 40GB storage (7B model)
- **Marketing VM**: 2 vCPU, 8GB RAM, 40GB storage (7B model)
- **Per Client Total**: 3 VMs, 6 vCPU, 20GB RAM, 130GB storage
- **Network**: Each VM needs public IP address
- **Client Isolation**: Complete VM set dedicated per business client

### Future Phase Resources
- **Sales Agent**: 2 vCPU, 8GB RAM, 20GB storage
- **CEO Agent**: 4 vCPU, 12GB RAM, 80GB storage (with SecretAI)

---

## Security Model Summary

### Trust Boundaries
- **Trusted**: TEE hardware, VMS-signed messages, verified agents, encrypted data
- **Untrusted**: Host OS, network, unsigned messages, unverified agents
- **Verification**: Hardware attestation + VMS cryptographic proof + message signatures

### Message Verification Model
- **Every Message Signed**: All cross-VM communication cryptographically signed with ed25519
- **Verifiable AI Provenance**: Cryptographic proof responses came from verified TEE-protected agents
- **Customer Receipt**: Each response includes signature and attestation verification
- **Audit Trail**: Complete cryptographic record of all AI-generated insights

### Key Management
- **Generation**: ed25519 keys generated within TEE via SecretVM, never exported
- **Distribution**: Hub maintains verified public keys from spoke attestation registration
- **Communication**: All cross-VM messages signed with TEE-generated private keys
- **Rotation**: Weekly key rotation with graceful transition period

### Data Protection
- **At Rest**: Encrypted within TEE
- **In Transit**: Encrypted with agent public keys
- **In Processing**: Never leaves TEE boundaries
- **Access Control**: Attestation-based authorization

---

*Last Updated: December 2024*  
*Document Owner: Boardroom TEE Development Team*  
*Purpose: Claude AI code generation reference - Standalone VM Architecture*