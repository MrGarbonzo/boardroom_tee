# Hub Architecture - The Brain

## Overview
The hub serves as the central data repository and orchestration layer for the Boardroom TEE system. It manages data ingestion, organization, and secure distribution to spoke agents.

---

## Core Components

### 1. Data Ingestion Pipeline
**Purpose**: Secure upload and initial processing of company data

**Components**:
- **Upload Endpoints**: Encrypted file upload with progress tracking
- **File Validation**: Type detection, size limits, malware scanning
- **Storage Layer**: Encrypted storage with client isolation
- **Processing Queue**: Batch processing queue for TinyLlama

**Infrastructure Requirements**:
- **Instance Size**: Medium (2 vCPU, 4GB RAM, expanded storage)
- **Storage**: TB+ storage per client (negotiate with TEE provider)
- **Security**: TEE environment with verifiable message signing

### 2. TinyLlama Data Organizer
**Purpose**: Intelligent categorization and indexing of uploaded data

**Processing Pipeline**:
1. **File Type Detection**: PDF, Excel, CSV, Word, TXT, Email identification
2. **Content Extraction**: Plain text extraction without complex parsing
3. **Content Analysis**: TinyLlama reads and understands extracted text
4. **Classification**: Assign categories based on content patterns

**Categories Assigned**:
- **Department**: Finance, Marketing, Sales, Operations, Other
- **Document Type**: Report, Data/Spreadsheet, Email, Planning, Contract
- **Time Period**: Extract obvious dates mentioned in content
- **Key Terms**: 5-10 primary keywords for search/retrieval

**Processing Timeline**: 2-24 hours for thorough batch processing

### 3. Agent Registry & Orchestration
**Purpose**: Manage spoke agent capabilities and route requests

**Registry Components**:
- **Agent Capabilities**: What each spoke agent can analyze
- **Attestation Status**: Current verification status of each agent
- **Performance Metrics**: Response times and success rates
- **Routing Logic**: Smart routing for multi-agent workflows

**Orchestration Features**:
- **Request Routing**: \"Who can analyze customer acquisition costs?\"
- **Context Management**: Preserve context through agent chains
- **Circular Dependency Prevention**: Avoid infinite loops
- **Cost Tracking**: Monitor agent usage for billing

### 4. Security & Communication Layer
**Purpose**: Verifiable message signing and secure data distribution

**Key Generation**:
```yaml
# Docker Compose Integration
services:
  boardroom-hub:
    volumes:
      - ./crypto/docker_private_key_ed25519.pem:/app/data/privkey.pem
      - ./crypto/docker_public_key_ed25519.pem:/app/data/pubkey.pem
      - ./crypto/docker_attestation_ed25519.txt:/app/data/quote.txt
```

**Communication Flow**:
1. Spoke agent startup with key generation
2. Agent registration with attestation quote
3. Hub verification of agent identity
4. Encrypted data transfer using verified public keys

---

## Data Storage Architecture

### Client Isolation Model
- **Dedicated VM per client**: Complete data isolation
- **Encrypted storage**: All data encrypted at rest within TEE
- **Metadata separation**: Client data never cross-contaminated
- **Audit trails**: Complete logging of data access

### Data Organization Structure
```
/client_data/
├── raw_uploads/           # Original uploaded files
├── processed_content/     # Extracted text content
├── metadata/             # TinyLlama categorization
├── indexes/              # Search and retrieval indexes
└── audit_logs/           # Access and processing logs
```

### Storage Optimization
- **Hot data**: Recently accessed, kept in memory
- **Warm data**: Frequently accessed, fast storage
- **Cold data**: Archive storage for older files
- **Compression**: Efficient storage of processed content

---

## API Endpoints

### Data Management APIs
```
POST /upload                    # Secure file upload
GET  /processing_status/{id}    # Check TinyLlama processing status
GET  /data_summary             # Overview of organized data
POST /data_query               # Natural language data requests
```

### Agent Management APIs
```
POST /agent/register           # Agent registration with attestation
GET  /agent/capabilities       # Available agent capabilities
POST /agent/request_data       # Agent data requests
POST /agent/collaborate        # Agent-to-agent communication
```

### Administration APIs
```
GET  /health                   # Hub health status
GET  /metrics                  # Performance and usage metrics
POST /client/onboard          # New client setup
GET  /audit_trail             # Access logging and compliance
```

---

## Performance Requirements

### Processing Targets
- **File Upload**: < 30 seconds for 100MB files
- **TinyLlama Processing**: 2-24 hours for complete analysis
- **Agent Data Requests**: < 5 seconds for standard queries
- **Complex Multi-Agent**: < 60 seconds for collaboration chains

### Scalability Metrics
- **Concurrent Agents**: Support 10+ simultaneous spoke agents
- **Data Volume**: Handle TB+ datasets per client
- **Query Throughput**: 100+ queries per hour per client
- **Uptime Target**: 99.9% availability

---

## Security Specifications

### TEE Requirements
- **Platform**: SecretVM with TDX support
- **Key Generation**: ed25519 or secp256k1 within TEE
- **Attestation**: Verifiable message signing for all communications
- **Memory Protection**: All processing within TEE boundaries

### Data Protection
- **Encryption at Rest**: All stored data encrypted within TEE
- **Encryption in Transit**: Verifiable message signing for all transfers
- **Access Control**: Attestation-based agent verification
- **Audit Compliance**: Complete activity logging

### Threat Model
- **Trusted**: TEE hardware, client data, verified spoke agents
- **Untrusted**: Host OS, network infrastructure, unverified agents
- **Mitigated**: MITM attacks, data exfiltration, malicious host access

---

## Error Handling & Recovery

### Processing Failures
- **Partial Processing**: Resume from last successful stage
- **Corruption Detection**: Hash verification and recovery
- **Resource Limits**: Graceful degradation under load
- **Manual Intervention**: Human review escalation paths

### Communication Failures
- **Agent Disconnection**: Automatic reconnection and state recovery
- **Attestation Expiry**: Background re-attestation processes
- **Network Issues**: Retry logic with exponential backoff
- **Key Rotation**: Seamless key update procedures

---

## Monitoring & Alerting

### Key Metrics
- **Processing Times**: TinyLlama categorization performance
- **Agent Health**: Spoke agent availability and response times
- **Storage Usage**: Client data volume and growth trends
- **Security Events**: Attestation failures and suspicious activity

### Alert Triggers
- **Processing Delays**: > 48 hour categorization times
- **Agent Failures**: Repeated attestation or communication failures
- **Storage Limits**: Approaching client storage quotas
- **Security Incidents**: Invalid attestation attempts

---

*Last Updated: [Current Date]*  
*Related: spoke_agents.md, security_model.md, api_specifications.md*
