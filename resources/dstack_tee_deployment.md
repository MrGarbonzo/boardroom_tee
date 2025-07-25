# dstack TEE Deployment Resources

## Overview
dstack is a developer-friendly and security-first SDK that simplifies the deployment of arbitrary containerized apps into Trusted Execution Environments (TEE). This resource provides comprehensive information for deploying Boardroom TEE components using the dstack platform as an alternative to direct Docker deployment.

## Key Features
- **Secure Deployment**: Deploy containerized apps securely in TEE in minutes
- **Familiar Tools**: Use familiar tools - just write a docker-compose.yaml
- **Secret Management**: Safely manage secrets and sensitive data
- **ZT-HTTPS**: Expose services via automated TLS termination

## Architecture Components

### Core Services
- **dstack-vmm**: Service running in bare TDX host to manage CVMs
- **dstack-gateway**: Reverse proxy to forward TLS connections to CVMs
- **dstack-kms**: KMS server to generate keys for CVMs
- **dstack-guest-agent**: Service running in CVM to serve containers' key derivation and attestation requests
- **meta-dstack**: Yocto meta layer to build CVM guest images

## Prerequisites for Boardroom TEE Deployment
- Bare metal TDX server setup following canonical/tdx
- Public IPv4 address assigned to the machine
- At least 16GB RAM, 100GB free disk space (minimum for our multi-agent setup)
- A domain with DNS access for Zero Trust HTTPS setup
- Additional 32GB+ RAM recommended for our multi-model deployment

## Installation Dependencies
```bash
# For Ubuntu 24.04
sudo apt install -y build-essential chrpath diffstat lz4 wireguard-tools xorriso

# Install Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
```

## Build Process for Boardroom TEE Integration

### 1. Build dstack Artifacts
```bash
git clone https://github.com/Dstack-TEE/meta-dstack.git --recursive
cd meta-dstack/
mkdir build
cd build
../build.sh hostcfg
```

### 2. Configure for Boardroom TEE
Edit `build-config.sh` to configure for our multi-agent architecture:
```bash
# Network configuration for Boardroom TEE
HUB_PORT=8080
FINANCE_PORT=8081
MARKETING_PORT=8082
SALES_PORT=8083
CEO_PORT=8084

# Attestation ports
HUB_ATTESTATION_PORT=29343
FINANCE_ATTESTATION_PORT=29344
MARKETING_ATTESTATION_PORT=29345
SALES_ATTESTATION_PORT=29346
CEO_ATTESTATION_PORT=29347

# Domain setup for Zero Trust HTTPS
BASE_DOMAIN=boardroom-tee.your-domain.com
```

### 3. Guest Image Options
**Option A: Download**
```bash
../build.sh dl 0.5.2
```

**Option B: Build from source**
```bash
../build.sh guest
```

### 4. Run dstack Components
Start three components in separate terminals:
- KMS: `./dstack-kms -c kms.toml`
- Gateway: `sudo ./dstack-gateway -c gateway.toml`
- VMM: `./dstack-vmm -c vmm.toml`

## Boardroom TEE Deployment with dstack

### Hub Deployment
Create `hub-docker-compose.yaml` for dstack deployment:
```yaml
version: '3'
services:
  boardroom-hub:
    image: hub-boardroom-tee:latest
    environment:
      - HUB_MODEL_NAME=meta-llama/Llama-3.2-1B-Instruct
      - HUB_MAX_MEMORY_MB=3000
      - HUB_API_PORT=8080
      - HUB_ATTESTATION_PORT=29343
      - CLIENT_ID=${CLIENT_ID}
    ports:
      - "8080:8080"
      - "29343:29343"
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
      - ./config:/app/config
      - /var/run/dstack.sock:/var/run/dstack.sock
    restart: always
```

### Finance Agent Deployment
Create `finance-docker-compose.yaml`:
```yaml
version: '3'
services:
  finance-agent:
    image: finance-boardroom-tee:latest
    environment:
      - AGENT_TYPE=finance
      - AGENT_MODEL_NAME=AdaptLLM/finance-LLM
      - AGENT_API_PORT=8081
      - AGENT_ATTESTATION_PORT=29344
      - AGENT_MAX_MEMORY_MB=7000
      - CLIENT_ID=${CLIENT_ID}
      - HUB_ENDPOINT=https://hub-${CLIENT_ID}.boardroom-tee.your-domain.com
    ports:
      - "8081:8081"
      - "29344:29344"
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
      - ./config:/app/config
      - /var/run/dstack.sock:/var/run/dstack.sock
    restart: always
```

### Marketing Agent Deployment
Create `marketing-docker-compose.yaml`:
```yaml
version: '3'
services:
  marketing-agent:
    image: marketing-boardroom-tee:latest
    environment:
      - AGENT_TYPE=marketing
      - AGENT_MODEL_NAME=mistralai/Mistral-7B-Instruct-v0.3
      - AGENT_API_PORT=8082
      - AGENT_ATTESTATION_PORT=29345
      - AGENT_MAX_MEMORY_MB=4000
      - CLIENT_ID=${CLIENT_ID}
      - HUB_ENDPOINT=https://hub-${CLIENT_ID}.boardroom-tee.your-domain.com
    ports:
      - "8082:8082"
      - "29345:29345"
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
      - ./config:/app/config
      - /var/run/dstack.sock:/var/run/dstack.sock
    restart: always
```

## TDX Quote Integration for Boardroom TEE

### Enhanced Attestation in Containers
Mount the dstack socket in all Boardroom TEE components:
```yaml
volumes:
  - /var/run/dstack.sock:/var/run/dstack.sock
```

### Request TDX Quotes for Attestation
```python
# src/shared/dstack_attestation.py
import requests
import json
import hashlib
from typing import Dict, Optional

class DstackAttestationClient:
    """Enhanced attestation client using dstack TDX quotes"""
    
    def __init__(self, socket_path: str = "/var/run/dstack.sock"):
        self.socket_path = socket_path
    
    async def get_tdx_quote(self, report_data: str) -> Dict:
        """Get TDX quote from dstack guest agent"""
        try:
            # The report_data is hashed with sha256 before passing to TDX
            response = requests.get(
                f"http://localhost/GetQuote?report_data={report_data}",
                unix_socket=self.socket_path
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"Failed to get quote: {response.status_code}")
                
        except Exception as e:
            raise Exception(f"TDX quote request failed: {str(e)}")
    
    async def generate_agent_attestation(self, agent_id: str, 
                                       public_key: str) -> Dict:
        """Generate attestation for Boardroom TEE agent"""
        # Create report data with agent identity and public key
        agent_data = {
            "agent_id": agent_id,
            "public_key": public_key,
            "timestamp": int(time.time())
        }
        
        # Convert to hex string for TDX quote
        report_data = json.dumps(agent_data, sort_keys=True)
        report_data_hex = "0x" + report_data.encode().hex()
        
        # Get TDX quote
        quote_response = await self.get_tdx_quote(report_data_hex)
        
        return {
            "agent_data": agent_data,
            "tdx_quote": quote_response,
            "verification_status": "pending"
        }
```

## Access Patterns for Boardroom TEE

### dstack Gateway Domain Mapping
Services are accessible via domain mapping:
- `hub-${CLIENT_ID}.boardroom-tee.domain.com` → Hub API (port 8080)
- `finance-${CLIENT_ID}.boardroom-tee.domain.com` → Finance Agent (port 8081)
- `marketing-${CLIENT_ID}.boardroom-tee.domain.com` → Marketing Agent (port 8082)
- `sales-${CLIENT_ID}.boardroom-tee.domain.com` → Sales Agent (port 8083)
- `ceo-${CLIENT_ID}.boardroom-tee.domain.com` → CEO Agent (port 8084)

### Attestation Endpoints
- `hub-${CLIENT_ID}-29343.boardroom-tee.domain.com` → Hub Attestation
- `finance-${CLIENT_ID}-29344.boardroom-tee.domain.com` → Finance Attestation
- And so on for each agent...

## Zero Trust HTTPS for Boardroom TEE

### Cloudflare Integration
Configure in `build-config.sh`:
```bash
# Cloudflare configuration for Boardroom TEE domain
CF_ZONE_ID=your_zone_id
CF_API_TOKEN=your_api_token
ACME_URL=https://acme-v02.api.letsencrypt.org/directory

# Base domain for all Boardroom TEE deployments
BASE_DOMAIN=boardroom-tee.your-domain.com

# Certificate paths
GATEWAY_CERT=${CERBOT_WORKDIR}/live/cert.pem
GATEWAY_KEY=${CERBOT_WORKDIR}/live/key.pem
```

### Launch Certbot for Automated TLS
```bash
# Generate certificates for all Boardroom TEE subdomains
RUST_LOG=info,certbot=debug ./certbot renew -c certbot.toml
```

### Certificate Transparency Monitoring
Monitor unauthorized certificates for your Boardroom TEE domain:
```bash
./ct_monitor -t https://localhost:9010/prpc -d boardroom-tee.your-domain.com
```

## Container Log Access for Boardroom TEE

### Centralized Logging
```bash
# Hub logs
curl 'http://hub-${CLIENT_ID}.boardroom-tee.domain.com:9090/logs/boardroom-hub?since=0&until=0&follow=true&text=true&timestamps=true&bare=true'

# Finance agent logs
curl 'http://finance-${CLIENT_ID}.boardroom-tee.domain.com:9090/logs/finance-agent?since=0&until=0&follow=true&text=true&timestamps=true&bare=true'

# Marketing agent logs
curl 'http://marketing-${CLIENT_ID}.boardroom-tee.domain.com:9090/logs/marketing-agent?since=0&until=0&follow=true&text=true&timestamps=true&bare=true'
```

### Log Parameters
- `since=0`: Starting Unix timestamp
- `until=0`: Ending Unix timestamp  
- `follow`: Continuous streaming
- `text`: Human-readable format
- `timestamps`: Add timestamps
- `bare`: Raw log lines without JSON

## Deployment Workflow for Boardroom TEE

### Step 1: Prepare dstack Environment
```bash
# Build dstack components
cd meta-dstack/build
../build.sh hostcfg
# Edit build-config.sh for Boardroom TEE configuration
../build.sh
```

### Step 2: Start dstack Services
```bash
# Terminal 1: KMS
./dstack-kms -c kms.toml

# Terminal 2: Gateway  
sudo ./dstack-gateway -c gateway.toml

# Terminal 3: VMM
./dstack-vmm -c vmm.toml
```

### Step 3: Deploy Boardroom TEE Components
Access dstack-vmm webpage at `http://localhost:9080`:
1. Upload `hub-docker-compose.yaml` first
2. Upload `finance-docker-compose.yaml`
3. Upload `marketing-docker-compose.yaml`
4. Upload remaining agent compose files as needed

### Step 4: Verify Deployment
```bash
# Check dstack gateway dashboard
open https://localhost:9070

# Verify Boardroom TEE services
curl https://hub-${CLIENT_ID}.boardroom-tee.domain.com/health
curl https://finance-${CLIENT_ID}.boardroom-tee.domain.com/health
curl https://marketing-${CLIENT_ID}.boardroom-tee.domain.com/health
```

## Security Enhancements with dstack

### Enhanced Secret Management
Pass encrypted environment variables for each agent:
```yaml
environment:
  - AGENT_PRIVATE_KEY=${ENCRYPTED_AGENT_KEY}
  - HUB_SHARED_SECRET=${ENCRYPTED_HUB_SECRET}
  - CLIENT_ENCRYPTION_KEY=${ENCRYPTED_CLIENT_KEY}
```

Variables are encrypted client-side and decrypted in the CVM before being passed to containers.

### TLS Passthrough for Agent Communication
Configure TLS passthrough for secure agent-to-agent communication:
```yaml
# Use 's' suffix for TLS passthrough
services:
  secure-agent-comm:
    # Maps to https://finance-${CLIENT_ID}-8443s.boardroom-tee.domain.com
    # TLS connection passed directly to agent, not terminated at gateway
```

## Common Troubleshooting for Boardroom TEE

### CID Conflicts with Multiple Agents
If you get "Address already in use" errors with multiple CVMs:
```bash
ps aux | grep 'guest-cid='
```
Update `vmm.toml` for larger CID pool:
```toml
[cvm]
cid_start = 33000
cid_pool_size = 5000  # Increased for multiple Boardroom TEE agents
```

### Memory Issues with Large Models
Monitor memory usage across all agents:
```bash
# Check memory usage via dstack dashboard
curl https://localhost:9070/api/memory-stats

# Check individual agent memory
curl https://hub-${CLIENT_ID}.boardroom-tee.domain.com/health
```

### Permission Issues (Ubuntu 23.10+)
```bash
sudo sysctl kernel.apparmor_restrict_unprivileged_userns=0
```

## Comparison: dstack vs Direct Docker Deployment

### Advantages of dstack for Boardroom TEE
- **Built-in TEE Integration**: Automatic TDX quote generation
- **Zero Trust HTTPS**: Automated TLS certificate management within TEE
- **Security-First**: Certificate transparency monitoring
- **Simplified Deployment**: Web UI for docker-compose deployment
- **Enhanced Attestation**: Direct access to hardware attestation features

### When to Use dstack vs Direct Docker
- **Use dstack**: For production deployments requiring hardware attestation
- **Use Direct Docker**: For development and testing environments
- **Hybrid Approach**: Development with Docker, production with dstack

## Integration with Existing Boardroom TEE Architecture

### Enhanced Attestation Service
```python
# src/attestation/dstack_enhanced_attestation.py
from src.shared.dstack_attestation import DstackAttestationClient
from src.attestation.attestation_client import SpokeAttestationClient

class EnhancedBoardroomAttestationClient(SpokeAttestationClient):
    """Enhanced attestation using dstack TDX quotes"""
    
    def __init__(self, agent_id: str, hub_discovery_endpoint: str):
        super().__init__(agent_id, hub_discovery_endpoint)
        self.dstack_client = DstackAttestationClient()
    
    async def generate_hardware_attestation(self) -> Dict:
        """Generate hardware-backed attestation using dstack"""
        # Use dstack TDX quote for hardware attestation
        attestation = await self.dstack_client.generate_agent_attestation(
            self.agent_id, 
            self.public_key_pem
        )
        
        # Combine with existing SecretGPT attestation
        combined_attestation = {
            "agent_id": self.agent_id,
            "hardware_attestation": attestation,
            "software_attestation": self.attestation_quote,
            "verification_chain": "dstack-tdx-secretgpt"
        }
        
        return combined_attestation
```

## Production Deployment Checklist

### Security Configuration
- [ ] Configure CAA records for certificate authority restrictions
- [ ] Set up Certificate Transparency monitoring
- [ ] Enable TLS passthrough for agent-to-agent communication
- [ ] Configure encrypted environment variables for all secrets

### Infrastructure Setup
- [ ] Provision bare metal TDX server with adequate resources
- [ ] Configure domain and DNS for Zero Trust HTTPS
- [ ] Set up Cloudflare integration for automated certificates
- [ ] Configure backup and monitoring systems

### Boardroom TEE Deployment
- [ ] Build and deploy dstack components
- [ ] Deploy Hub with Llama-3.2-1B-Instruct
- [ ] Deploy Finance Agent with AdaptLLM/Finance-LLM-7B
- [ ] Deploy Marketing Agent with Mistral-7B-Instruct-v0.3
- [ ] Deploy additional agents as needed
- [ ] Verify all inter-agent attestation chains

### Monitoring and Maintenance
- [ ] Set up centralized logging collection
- [ ] Configure memory and performance monitoring
- [ ] Implement automated certificate renewal
- [ ] Set up alerting for attestation failures

---

## Related Documentation
- [`docker_implementation.md`](./docker_implementation.md) - Direct Docker deployment approach
- [`distributed_attestation_plan.md`](./distributed_attestation_plan.md) - Attestation architecture
- [`deployment_structure.md`](./deployment_structure.md) - Overall deployment structure
- [`hub_architecture.md`](./hub_architecture.md) - Hub component details

## Community & Resources
- dstack Repository: https://github.com/Dstack-TEE/meta-dstack
- Open source project by Phala Network
- Apache License 2.0
- SecretGPT Integration: F:/coding/secretGPT_attestai_1.0/

---

*Last Updated: [Current Date]*  
*Document Owner: Boardroom TEE Team*  
*Version: 1.0 - dstack Integration Guide*