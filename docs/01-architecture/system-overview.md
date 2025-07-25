# System Overview - Boardroom TEE Architecture

## Core Innovation: Agent-to-Agent Collaborative Network

### Breakthrough Concept
Instead of fixed pipeline processing, spoke agents communicate with each other through the hub to provide collaborative specialist analysis on-demand.

**Traditional Approach**: Question → Fixed Pipeline → Answer  
**Boardroom TEE**: Question → Dynamic Agent Network → Collaborative Answer

### MVP Collaboration Example (Phase 1)
1. **CFO asks**: "What's the ROI on our $500K Q4 holiday marketing campaign?"
2. **Marketing agent** analyzes campaign performance, customer acquisition, conversion rates
3. **Finance agent** calculates ROI metrics, payback period, budget impact (using Marketing context)
4. **Hub synthesizes** both analyses into comprehensive ROI assessment

### Future Phase Collaboration
- **3-way workflows**: Marketing → Sales → Finance analysis chains
- **Strategic synthesis**: CEO agent combining all department insights

### Competitive Advantages
- **Dynamic Multi-Specialist Analysis**: Adaptive routing vs fixed processing stages
- **Cost Efficiency**: Only pay for agents actually used in each query
- **Flexible Workflows**: Natural conversation flow vs rigid pipeline sequence
- **Scalable Architecture**: Add new specialists without rebuilding core system
- **Better User Experience**: Conversational vs batch processing

---

## Component Architecture

### Hub - Central Data Repository & Orchestration
**Purpose**: Secure data storage, organization, and agent coordination
**Model**: Llama-3.2-1B-Instruct (unified for data processing + orchestration)
**Instance**: Medium (2 vCPU, 4GB RAM, TB+ storage)

**Core Functions**:
- Encrypted data storage with client isolation
- TinyLlama-based document categorization and indexing
- Agent registry and capability discovery
- Secure communication brokering between agents
- Attestation verification and audit logging

### Spoke Agents - Domain Specialists

#### Finance Agent (MVP Phase 1)
- **Model**: AdaptLLM/Finance-LLM-7B (specialized financial model)
- **Instance**: Medium (2 vCPU, 8GB RAM, 40GB storage)
- **Specialization**: Financial analysis, budget planning, ROI calculation, risk assessment
- **Key Strength**: Domain-specific financial expertise

#### Marketing Agent (MVP Phase 1)
- **Model**: Mistral-7B-Instruct-v0.3 (general-purpose 7B model)
- **Instance**: Medium (2 vCPU, 8GB RAM, 20GB storage)
- **Specialization**: Campaign analysis, customer segmentation, market research
- **Key Strength**: Versatile marketing intelligence

#### Sales Agent (Future Phase 2)
- **Model**: Mistral-7B-Instruct-v0.3
- **Instance**: Medium (2 vCPU, 8GB RAM, 20GB storage)
- **Specialization**: Pipeline forecasting, lead scoring, territory optimization

#### CEO Agent (Future Phase 3)
- **Model**: deepseek-ai/deepseek-llm-7b-chat with SecretAI integration
- **Instance**: Large (4 vCPU, 12GB RAM, 80GB storage)
- **Specialization**: Strategic synthesis, cross-departmental insights, board-level analysis

---

## Data Flow Architecture

### Data Ingestion (Push Model)
```
Company Data Upload → Hub Encrypted Storage → TinyLlama Processing (2-24h) → 
Indexed Data → Agent Requests → Secure Distribution → Analysis → Insights
```

### Agent Collaboration Flow
```
Agent A Query → Hub Capability Discovery → Agent B Identification → 
Attestation Verification → Secure Data Transfer → Analysis → 
Context-Preserved Response → Multi-Agent Synthesis
```

### Security Flow
```
TEE Key Generation → Agent Registration → Attestation Verification → 
Encrypted Communication → Audit Logging → Re-attestation (4-6h)
```

---

## Communication Protocols

### Verifiable Message Signing
**Foundation**: SecretVM platform with built-in verifiable message signing
**Key Generation**: Each TEE generates ed25519/secp256k1 key pairs inside secure environment
**Attestation Binding**: Public keys embedded in attestation quotes tied to specific keys
**Hardware Protection**: Private keys never leave TEE, protected from malicious host OS

### Agent Registration Process
1. **Agent Startup**: Generate key pair inside TEE
2. **Attestation Creation**: Public key embedded in attestation quote
3. **Hub Registration**: Agent sends public key + attestation to hub
4. **Hub Verification**: Validates attestation and stores verified public key
5. **Secure Communication**: Hub encrypts data using agent's verified public key

### Agent-to-Agent Communication
1. **Discovery Request**: Agent A asks hub "who can analyze X?"
2. **Capability Matching**: Hub identifies best Agent B for task
3. **Attestation Exchange**: Hub facilitates secure key exchange
4. **Direct Communication**: Agents communicate directly using verified keys
5. **Context Preservation**: Multi-hop verification ensures TEE security throughout chain

---

## Deployment Model

### Client Isolation
- **Dedicated VMs**: Each client gets separate VM instances
- **Complete Data Separation**: No data cross-contamination between clients
- **Independent Scaling**: Scale agents based on individual client needs
- **Flexible Pricing**: Deploy only needed agents per client

### Modular Architecture
```
F:/coding/boardroom_tee/
├── hub/                    # Central orchestration
├── spoke_finance/          # Financial analysis
├── spoke_marketing/        # Marketing intelligence
├── spoke_sales/           # Sales optimization
├── spoke_ceo/             # Strategic synthesis (premium)
└── docs/                  # Implementation documentation
```

### Network Architecture
- **Internal Communication**: Secure attestation-verified messaging
- **External Access**: Hub exposes public API
- **Port Allocation**: Dedicated ports per component (8080-8084)
- **Attestation Ports**: Separate ports for verification (29343-29347)

---

## Security Model

### Trust Boundaries
- **Trusted**: TEE hardware, verified agents, encrypted data within TEE
- **Untrusted**: Host OS, network infrastructure, unverified agents
- **Verification**: Hardware attestation + cryptographic proof of TEE execution

### Threat Model
- **Protected Against**: Host OS compromise, network eavesdropping, data exfiltration
- **Mitigated**: MITM attacks via attestation verification
- **Monitored**: All agent communications logged for audit compliance

### Compliance Features
- **Audit Trails**: Complete logging of data access and agent interactions
- **Data Sovereignty**: Client data never leaves their dedicated TEE environment
- **Cryptographic Proof**: Verifiable evidence of secure processing
- **Regulatory Support**: SOC2, GDPR, HIPAA compliance capabilities

---

## Performance Characteristics

### Processing Targets
- **Document Upload**: < 30 seconds for 100MB files
- **TinyLlama Categorization**: 2-24 hours for complete analysis
- **Agent Queries**: < 5 seconds for standard requests
- **Multi-Agent Collaboration**: < 60 seconds for complex workflows

### Scalability Metrics
- **Concurrent Agents**: 10+ simultaneous spoke agents per client
- **Data Volume**: TB+ datasets per client deployment
- **Query Throughput**: 100+ queries per hour per client
- **Collaboration Chains**: Support 5+ agent collaboration sequences

### Resource Optimization
- **Memory Management**: Model-specific memory allocation and cleanup
- **Caching**: Frequent collaboration patterns cached for performance
- **Load Balancing**: Intelligent routing based on agent availability
- **Cost Tracking**: Monitor agent usage for billing optimization

---

## Business Model Integration

### Pricing Tiers
- **MVP Tier**: Hub + Finance + Marketing agents with collaboration ($30K-50K/year)
- **Expanded Tier**: Add Sales agent for 3-way workflows ($60K-80K/year)
- **Enterprise Tier**: Add CEO agent with SecretAI integration ($100K-150K/year)

### Value Proposition
- **Privacy-First**: Secure access to ALL company data with TEE guarantees
- **Multi-Specialist Intelligence**: Collaborative analysis vs single AI responses
- **Cost Advantage**: AI specialist consultation vs $50K-200K traditional consulting
- **Data Completeness**: Access to complete datasets vs limited consulting data access

---

*Last Updated: December 2024*  
*Related: [`02-implementation/`](../02-implementation/) for building instructions*  
*Purpose: Foundation reference for Claude code generation*