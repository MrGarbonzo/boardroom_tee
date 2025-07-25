# Configuration Reference - Boardroom TEE

## Environment Variables

### Hub Configuration
```bash
# Model and processing
HUB_MODEL_NAME=meta-llama/Llama-3.2-1B-Instruct
HUB_MAX_MEMORY_MB=3000
HUB_API_PORT=8080
HUB_ATTESTATION_PORT=29343

# Client and logging
CLIENT_ID=client-unique-identifier
LOG_LEVEL=INFO
AUDIT_ENABLED=true

# Storage and processing
MAX_STORAGE_GB=1000
PROCESSING_TIMEOUT_HOURS=24
SUPPORTED_FILE_TYPES=pdf,docx,xlsx,csv,txt,eml
```

### Agent Configuration (Finance Agent Example)
```bash
# Agent identity
AGENT_TYPE=finance
AGENT_MODEL_NAME=AdaptLLM/finance-LLM
AGENT_API_PORT=8081
AGENT_ATTESTATION_PORT=29344
AGENT_MAX_MEMORY_MB=7000

# Hub connection
HUB_ENDPOINT=https://hub-domain:8080
HUB_ATTESTATION_ENDPOINT=https://hub-domain:29343

# TEE settings
TEE_PLATFORM=secretvm
ATTESTATION_REQUIRED=true
```

---

## Port Allocation

### Standard Port Assignment
```
Hub:            8080 (API), 29343 (attestation)
Finance Agent:  8081 (API), 29344 (attestation)
Marketing:      8082 (API), 29345 (attestation)
Sales:          8083 (API), 29346 (attestation)
CEO:            8084 (API), 29347 (attestation)
```

### Network Configuration
```yaml
# docker-compose network setup
networks:
  boardroom-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16
```

---

## Resource Requirements

### Minimum System Requirements
```
Total RAM: 32GB (for full deployment)
Storage: 500GB SSD per client
CPU: 8 cores minimum
TEE: Intel TDX or AMD SEV support
Network: 1Gbps connection recommended
```

### MVP Resource Allocation (Phase 1)
```yaml
# Hub resources
hub:
  memory: 4GB
  cpu: 2 cores
  storage: TB+ (client data)

# Finance Agent (AdaptLLM 7B model)
finance_agent:
  memory: 8GB
  cpu: 2 cores
  storage: 40GB
  model: "AdaptLLM/finance-LLM"

# Marketing Agent (Mistral 7B model)
marketing_agent:
  memory: 8GB
  cpu: 2 cores
  storage: 20GB
  model: "mistralai/Mistral-7B-Instruct-v0.3"
```

### Future Phase Resources
```yaml
# Sales Agent (Phase 2)
sales_agent:
  memory: 8GB
  cpu: 2 cores
  storage: 20GB
  model: "mistralai/Mistral-7B-Instruct-v0.3"

# CEO Agent (Phase 3 with SecretAI)
ceo_agent:
  memory: 12GB
  cpu: 4 cores
  storage: 80GB
  model: "deepseek-ai/deepseek-llm-7b-chat"
  special_features: "SecretAI integration"
```

---

## Model Specifications

### LLM Models by Component
```yaml
models:
  hub:
    name: "meta-llama/Llama-3.2-1B-Instruct"
    parameters: "1.2B"
    memory_usage: "~3GB"
    purpose: "Data organization + orchestration"
  
  finance_agent:
    name: "AdaptLLM/finance-LLM"
    parameters: "7B"
    memory_usage: "~7GB"
    purpose: "Financial analysis and calculations"
  
  marketing_agent:
    name: "mistralai/Mistral-7B-Instruct-v0.3"
    parameters: "7B"
    memory_usage: "~7GB"
    purpose: "Marketing intelligence and analysis"
  
  sales_agent:
    name: "mistralai/Mistral-7B-Instruct-v0.3"
    parameters: "7B"
    memory_usage: "~7GB"
    purpose: "Sales optimization and forecasting"
  
  ceo_agent:
    name: "deepseek-ai/deepseek-llm-7b-chat"
    parameters: "7B"
    memory_usage: "~10GB"
    purpose: "Strategic synthesis and executive insights"
```

---

## Security Configuration

### TEE Settings
```yaml
tee_config:
  platform: "secretvm"
  key_type: "ed25519"
  attestation_validity_hours: 4
  re_attestation_interval: "3.5 hours"
  measurement_verification: true
```

### Cryptographic Standards
```yaml
crypto_standards:
  signing_algorithm: "Ed25519"
  encryption_algorithm: "AES-256-GCM"
  key_derivation: "HKDF-SHA256"
  hash_algorithm: "SHA-256"
```

---

## Troubleshooting Quick Reference

### Common Commands
```bash
# Health checks
curl http://localhost:8080/health  # Hub
curl http://localhost:8081/health  # Finance
curl http://localhost:8082/health  # Marketing

# Container logs
docker logs boardroom-hub-${CLIENT_ID}
docker logs finance-agent-${CLIENT_ID}

# Resource monitoring
docker stats --filter name=${CLIENT_ID}

# TEE device check
ls -la /dev/sgx_*
sudo dmesg | grep -i tdx
```

### Error Resolution
```bash
# Memory issues
docker system prune -f
# Restart with lower memory limits

# TEE device access
sudo chmod 666 /dev/sgx_enclave
sudo chmod 666 /dev/sgx_provision

# Attestation failures
# Check measurement values in logs
# Verify TEE platform compatibility
```

---

## Deployment Phases

### Phase 1: MVP Configuration
```yaml
mvp_deployment:
  components: ["hub", "finance_agent", "marketing_agent"]
  total_memory: "20GB"
  total_storage: "100GB"
  collaboration_enabled: true
  key_demo: "Finance-Marketing ROI analysis"
  pricing: "$25K-40K/year"
  models:
    - "Llama-3.2-1B-Instruct (hub)"
    - "AdaptLLM/finance-LLM (7B)"
    - "Mistral-7B-Instruct-v0.3 (7B)"
```

### Phase 2: Expanded Configuration
```yaml
expanded_deployment:
  components: ["hub", "finance_agent", "marketing_agent", "sales_agent"]
  total_memory: "28GB"
  total_storage: "140GB"
  collaboration_enabled: true
  three_way_workflows: true
  pricing: "$40K-60K/year"
```

### Phase 3: Enterprise Configuration
```yaml
enterprise_deployment:
  components: ["hub", "finance_agent", "marketing_agent", "sales_agent", "ceo_agent"]
  total_memory: "40GB"
  total_storage: "220GB"
  collaboration_enabled: true
  secretai_integration: true
  strategic_synthesis: true
  pricing: "$75K-150K/year"
```

---

*Last Updated: December 2024*  
*Purpose: Quick reference for Claude code generation and deployment*