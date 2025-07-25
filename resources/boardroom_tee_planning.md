# Boardroom TEE - Hub and Spoke AI System Planning

## Project Overview
Building a TEE-based AI system where executives can get insights from ALL company data with guaranteed privacy. Uses hub-and-spoke architecture with **agent-to-agent collaboration** to optimize costs and deliver multi-specialist analysis dynamically.

## Core Innovation: Agent-to-Agent Collaborative Network

**Breakthrough Concept**: Instead of fixed pipeline processing, spoke agents can communicate with each other through the hub to provide collaborative specialist analysis on-demand.

**How It Works**:
- CEO asks: "Should we acquire Company X?"
- Finance agent performs valuation analysis
- Legal agent does due diligence review (with Finance context)
- Technology agent assesses integration (with Legal + Finance context) 
- Sales agent analyzes market impact (with all previous context)

**Competitive Advantages**:
- **Dynamic Multi-Specialist Analysis**: Same collaborative intelligence as 6-stage pipeline but adaptive
- **Cost Efficiency**: Only pay for agents actually used in each query
- **Flexible Workflows**: Natural conversation flow vs rigid pipeline sequence
- **Scalable Architecture**: Add new specialists without rebuilding core system
- **Better Than Traditional Pipeline**: Adaptive routing vs fixed processing stages

**Technical Implementation**:
- **Agent Registry**: Hub maintains capabilities of each spoke agent
- **Request Routing**: Agents ask hub "who can analyze X?" 
- **Brokered Communication**: Hub facilitates secure agent-to-agent requests via attestation
- **Context Preservation**: Multi-hop attestation ensures TEE security throughout chain
- **Result Integration**: Requesting agent combines specialist insights

**MVP Approach**: Start with basic hub-spoke, add agent-to-agent collaboration as core feature (not just future enhancement)

## Future Enhancement: 6-Stage Specialist Pipeline Integration

**Premium Content Roadmap**: After MVP validation, integrate the proven 6-stage specialist pipeline from enclave_consulting project

**6-Stage Pipeline Overview**:
1. **Universal Data Organizer** - Smart routing and industry detection
2. **Parallel Industry Specialists** - Multiple expert models analyzing independently  
3. **Quality Validation Gate** - Confidence scoring and anomaly detection
4. **Sequential Specialist Refinement** - Same specialists collaborate with context
5. **Context Synthesis** - Conflict resolution and priority ranking
6. **DeepSeek R1 Final Synthesis** - Executive-quality report generation

**Integration Strategy for Boardroom TEE**:
- **CEO Agent**: Full 6-stage pipeline for comprehensive business analysis (premium tier)
- **Department Agents**: Simplified 2-3 stage specialist processes
- **Value Hierarchy**: Clear differentiation between basic spoke agents and premium CEO analysis
- **Pricing Justification**: Multi-specialist consultation commands premium pricing

**Competitive Advantage**: "Your boardroom AI doesn't just access all your data - it processes it through multiple AI specialists who collaborate just like the best human consulting teams."

**Implementation Priority**: ~~Post-MVP, after validating basic hub-spoke architecture and securing initial customers~~ **UPDATED**: Agent-to-agent collaboration provides similar value with better flexibility - 6-stage pipeline becomes optional premium enhancement rather than core competitive advantage

### Business Model Implications

**Standalone Value Validation**: The project has significant value even without the 6-stage pipeline:
- **Privacy-first access to ALL company data** - Solves major C-suite pain point
- **TEE guarantees** - Cryptographically provable data security
- **Specialized departmental agents** - Domain-specific intelligence vs generic AI
- **Cross-departmental insights** - Finance agent sees marketing spend impact
- **Agent-to-agent collaboration** - Multi-specialist analysis without pipeline overhead

**Market Position**: Companies currently pay $50K-200K for traditional consulting with limited data access. Boardroom TEE offers secure access to complete datasets with specialist AI analysis.

**Value Hierarchy**:
- **Basic Tier**: Single department agents (CFO, Marketing, Sales) - $15K-30K/year
- **Premium Tier**: Multi-agent collaboration + CEO agent - $50K-100K/year  
- **Enterprise Tier**: Full 6-stage pipeline integration - $100K-200K/year

**Competitive Moat**: Agent-to-agent collaboration delivers multi-specialist intelligence with lower infrastructure costs and higher flexibility than fixed pipeline approaches.

---

## Hub and Spoke Model Architecture

### Central Hub (Enclave_Consulting Evolution)
**Purpose**: Secure data storage and routing hub
**Instance Size**: Small (1 vCPU, 2GB RAM, 20GB Storage)
**Key Functions**:
- Encrypted data storage for all company information
- Lightweight LLM for data understanding and routing
- Authentication and access control
- Secure API endpoints for spoke agents
- Audit trail and compliance logging
- Data indexing and search capabilities

**Hub Responsibilities**:
- Ingest and encrypt all company data sources
- Maintain data relationships and metadata
- Route relevant data to requesting spoke agents
- Ensure data isolation between different clients
- Provide attestation services for TEE compliance

### Spoke Agents (Domain-Specific)

#### 1. CFO Agent
**Instance Size**: Medium (2 vCPU, 4GB RAM, 40GB Storage)
**Data Focus**: Financial records, budgets, forecasts, expenses, revenue
**Capabilities**:
- Financial analysis and reporting
- Budget variance analysis
- Cash flow forecasting
- Risk assessment
- Compliance monitoring

#### 2. Marketing Agent  
**Instance Size**: Small (1 vCPU, 2GB RAM, 20GB Storage)
**Data Focus**: Customer data, campaigns, website analytics, social media
**Capabilities**:
- Campaign performance analysis
- Customer segmentation
- ROI calculations
- Market trend analysis
- Content strategy recommendations

#### 3. Sales Agent
**Instance Size**: Small (1 vCPU, 2GB RAM, 20GB Storage)  
**Data Focus**: CRM data, sales pipeline, customer interactions, deals
**Capabilities**:
- Pipeline forecasting
- Lead scoring and qualification
- Sales performance analysis
- Territory optimization
- Deal risk assessment

#### 4. CEO Agent (Premium Tier)
**Instance Size**: Large (4 vCPU, 8GB RAM, 80GB Storage)
**Data Focus**: All company data with strategic perspective
**Capabilities**:
- Full 6-stage pipeline analysis from enclave_consulting
- Cross-departmental insights
- Strategic recommendations
- Board presentation preparation
- Scenario planning and modeling

---

## Advantages of Hub-Spoke Model

### Cost Optimization
- Most agents run on small instances (cheap)
- Scale individual agents based on usage
- Only large instance for premium CEO agent
- Hub remains constant, lightweight cost

**Advantages of Agent-to-Agent Collaboration**:
- **Dynamic Routing**: Only specialists needed for each query get involved
- **On-Demand Scaling**: Spin up agents as needed vs running all simultaneously
- **Flexible Workflows**: Natural conversation flow adapts to business questions
- **Cost Efficiency**: Pay only for agents actually used in each analysis
- **Collaborative Intelligence**: Same multi-specialist value as 6-stage pipeline
- **Better User Experience**: Adaptive analysis vs rigid processing sequence
- **Infinite Scalability**: Add new specialist types without rebuilding architecture

**Technical Implementation for Agent-to-Agent**:
- **Multi-hop Attestation**: Hub verifies all agents in communication chain
- **Context Preservation**: Maintain TEE security through agent-to-agent requests
- **Circular Dependency Handling**: Smart routing to prevent infinite loops
- **Cost Tracking**: Monitor cross-agent calls for billing and optimization

---

## Data Flow Architecture

```
Company Data Sources → Hub (Encrypted Storage) → Spoke Agents → Insights
                          ↓
                    Authentication & Routing
                          ↓
                     Audit & Compliance
```

### Data Ingestion Process
1. Company uploads data to secure hub endpoint
2. Hub encrypts and stores data with metadata
3. Hub creates searchable index without exposing raw data
4. Hub maintains data lineage and relationships

### Agent Query Process
1. Spoke agent authenticates with hub
2. Agent requests specific data for analysis
3. Hub validates permissions and returns relevant encrypted data
4. Agent processes data locally in TEE environment
5. Agent returns insights while maintaining data privacy
6. Hub logs all access for audit trail

---

---

## The Brain (Hub) - Detailed Architecture

### TinyLlama Data Processing & Organization (Simplified Initial Version)

**File Type Processing Pipeline**:
1. **File Type Detection**: Identify file format using extensions and headers (PDF, Excel, CSV, Word, TXT, Email)
2. **Content Extraction**: Extract readable text content only
   - PDF → plain text content
   - Excel → cell values as text (no formulas/formatting)
   - CSV → raw data as text
   - Word → document text content
   - Email → subject + body text
   - No complex parsing of tables, charts, or formatting - just extract the words
3. **Content Analysis**: TinyLlama reads and understands the extracted text content
4. **Classification**: Assign categories based on content patterns TinyLlama identifies
   - "Mentions budgets and expenses" → Finance department
   - "Contains customer names and deal amounts" → Sales document
   - "Discusses campaign metrics" → Marketing report

**Simple Categories/Tags**:
- **Department**: Finance, Marketing, Sales, Operations, Other
- **Document Type**: Report, Data/Spreadsheet, Email, Planning, Contract
- **Time Period**: Extract obvious dates mentioned in content
- **Key Terms**: 5-10 primary keywords for search/retrieval

**Minimal Relationship Handling**:
- Tag documents mentioning same obvious entities (company names, email addresses)
- Simple "related documents" lists (no complex relationship graphs)
- Basic cross-referencing for common entities

**Essential Metadata Storage**:
- File name, type, upload date, processing date
- Primary department assignment
- Document type classification
- Basic topic keywords (5-10 terms max)
- File size and hash for integrity
- Any obvious dates found in content

**Processing Flow**:
1. Extract text from uploaded file
2. Identify department based on content keywords
3. Assign document type category
4. Extract 5-10 key terms for indexing
5. Note any obvious dates mentioned
6. Store with basic metadata for spoke retrieval

**Design Philosophy**: Keep initial version simple - let spoke agents do detailed analysis once they receive specific data from hub. Hub's job is organization and routing, not deep analysis.

### Data Upload Strategy
**Push Model**: Companies upload data to us (vs us pulling from their systems)
**Security Benefits**:
- No VPN connections or direct access to client infrastructure
- Companies control exactly what data gets shared
- Clear data boundaries and ownership
- Easier compliance and audit trails
- Cleaner liability model

**Legal Benefits**:
- Clear data transfer agreements
- Companies can sanitize/anonymize before upload
- Simpler GDPR/privacy law compliance
- Easier sales conversations ("upload your data" vs "give us access")

### Storage Requirements
**Current Constraint**: 80GB max (large instance)
**Reality Check**: Most companies need TB+ of storage
**Solution**: Get expanded storage from TEE provider
**Justification**: High-value, low-volume business model supports premium infrastructure costs

---

## Hub-Spoke Secure Communication

### Verifiable Message Signing Architecture
**Existing Infrastructure**: SecretVM platform includes built-in Verifiable Message Signing capability that solves secure communication elegantly.

**How Verifiable Message Signing Works**:
- **Key Generation**: Each TEE generates fresh key pair (ed25519 or secp256k1) inside the secure environment
- **Attestation Binding**: Public key is embedded in special attestation quote tied to that specific key
- **Hardware Protection**: Private key never leaves TEE, protected even from malicious host OS
- **Verifiable Trust**: Attestation quote provides cryptographic proof that keys were generated in genuine TEE

**Secure Communication Flow**:
1. **Spoke Agent Startup**: Generates key pair inside TEE using docker volume mounts
2. **Attestation Creation**: Public key embedded in attestation quote automatically
3. **Hub Registration**: Spoke sends public key + attestation quote to hub
4. **Hub Verification**: Validates attestation quote and extracts/stores verified public key
5. **Encrypted Communication**: Hub encrypts data using spoke's verified public key
6. **Decryption**: Only that specific TEE can decrypt with its private key

**Docker Compose Integration**:
```yaml
services:
  cfo-agent:
    volumes:
      - ./crypto/docker_private_key_ed25519.pem:/app/data/privkey.pem
      - ./crypto/docker_public_key_ed25519.pem:/app/data/pubkey.pem
      - ./crypto/docker_attestation_ed25519.txt:/app/data/quote.txt
```

**Agent-to-Agent Communication**:
- Each agent has its own verified key pair generated in TEE
- Hub brokers encrypted communication between agents using verified public keys
- Multi-hop verification ensures all agents in communication chain are legitimate TEEs
- Cryptographic keys directly bound to attestation (stronger than TLS certificates)

**Security Guarantees**:
- Private keys generated and stored entirely within TEE
- Public keys cryptographically bound to attestation quotes
- Hub can verify agent identity before sharing any data
- Even compromised host OS cannot access private keys
- Man-in-the-middle attacks prevented by attestation validation

**Implementation Recommendations**:
- **Re-attestation Frequency**: 4-6 hour intervals for active sessions
  - Balances security with performance (TEE environments relatively stable)
  - Use sliding window - re-attest when token halfway to expiration

- **Expired Attestation During Conversation**: Graceful degradation with background refresh
  - Hub warns spoke when attestation is 80% expired
  - Spoke generates new attestation in background
  - If expires mid-request: hub pauses data transfer, spoke provides fresh attestation, hub resumes
  - Fallback: if re-attestation fails, drop session but preserve conversation state for recovery

- **Spoke Restarts/Updates**: Planned vs unplanned restart handling
  - **Planned Updates**: Spoke signals "updating to v1.3", hub expects new measurements, pre-approve new versions
  - **Unplanned Restarts**: Spoke re-registers from scratch, hub treats as new session (security-first)
  - Conversation context can be restored after successful re-attestation

- **Performance Optimizations**:
  - Cache attestation certificates at hub to avoid repeated validation overhead
  - Use measurement whitelisting rather than exact matches for system variations

---

## Updated Data Flow

```
Company Data Upload → Hub (Encrypted Storage) → TinyLlama Processing (2-24h) → 
Indexed Data → Attestation-Verified Spoke Requests → Encrypted Data Transfer → 
Spoke Analysis → Insights
```

### Detailed Flow:
1. **Data Ingestion**: Company uploads via secure endpoints
2. **Initial Processing**: TinyLlama categorizes and indexes (batch, 2-24h)
3. **Spoke Request**: Agent requests data with attestation proof
4. **Hub Verification**: Validates spoke TEE status via attestation
5. **Secure Transfer**: Encrypted data sent only to verified spokes
6. **Local Processing**: Spoke processes data in TEE environment
7. **Results**: Insights returned while maintaining data privacy

---

## Next Steps to Plan
- [ ] Design agent registry and capability discovery system
- [ ] Plan multi-hop attestation architecture for agent-to-agent communication
- [ ] Define agent-to-agent communication protocols and APIs
- [ ] Create cost tracking and billing system for cross-agent requests
- [ ] Design circular dependency prevention and smart routing logic
- [ ] Plan agent specialization and domain expertise for each spoke
- [ ] Define pricing tiers and packaging for collaborative vs single-agent access
- [ ] Create technical implementation roadmap for agent collaboration
- [ ] Design user interfaces for agent orchestration and results

---

## Questions to Address
1. How do we prevent infinite loops in agent-to-agent communication chains?
2. What specific domain expertise should each agent type have?
3. How do we handle cost allocation when multiple agents collaborate on one query?
4. What's the optimal routing algorithm for multi-agent workflows?
5. How do we ensure context quality degrades gracefully through agent chains?
6. What monitoring and alerting do we need for agent collaboration performance?
7. How do we handle agent failures mid-collaboration?
8. What's the user experience for complex multi-agent workflows?
9. How do we validate agent-to-agent communication maintains TEE guarantees?
10. What compliance standards apply to multi-agent data processing?

---

## Technical Notes
- **Attestation Infrastructure**: Existing secretGPT attestation hub provides proven foundation
- **Processing Model**: Batch processing removes real-time complexity
- **Security Model**: Push data + attestation-based communication = strong security posture
- **Scalability**: Hub-spoke architecture allows independent scaling of each agent type

---

*Last Updated: [Current Date]*
*Document Owner: [Your Name]*
