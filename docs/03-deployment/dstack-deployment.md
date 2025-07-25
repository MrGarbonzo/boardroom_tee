# dstack TEE Platform Deployment

## Overview
Alternative deployment approach using the dstack platform for hardware TEE integration with automated certificate management and enhanced security features.

---

## Key Advantages for Boardroom TEE
- **Built-in TEE Integration**: Automatic TDX quote generation
- **Zero Trust HTTPS**: Automated TLS certificate management within TEE
- **Enhanced Attestation**: Direct access to hardware attestation features
- **Web UI Deployment**: Simple docker-compose.yaml upload interface

---

## Prerequisites
- Bare metal TDX server with 32GB+ RAM (for multiple 7B models)
- Public IPv4 address and domain access
- Ubuntu 24.04 LTS with TDX support

## Installation
```bash
# Install dependencies
sudo apt install -y build-essential chrpath diffstat lz4 wireguard-tools xorriso

# Install Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Clone and build dstack
git clone https://github.com/Dstack-TEE/meta-dstack.git --recursive
cd meta-dstack/build
../build.sh hostcfg
# Edit build-config.sh for Boardroom TEE
../build.sh
```

---

## Boardroom TEE Docker Compose for dstack

### Hub Deployment
```yaml
# hub-dstack-compose.yaml
version: '3'
services:
  boardroom-hub:
    image: hub-boardroom-tee:latest
    environment:
      - HUB_MODEL_NAME=meta-llama/Llama-3.2-1B-Instruct
      - CLIENT_ID=${CLIENT_ID}
    ports:
      - "8080:8080"
      - "29343:29343"
    volumes:
      - ./data:/app/data
      - /var/run/dstack.sock:/var/run/dstack.sock  # dstack integration
    restart: always
```

### Finance Agent Deployment
```yaml
# finance-dstack-compose.yaml
version: '3'
services:
  finance-agent:
    image: finance-boardroom-tee:latest
    environment:
      - AGENT_TYPE=finance
      - AGENT_MODEL_NAME=AdaptLLM/finance-LLM
      - AGENT_MAX_MEMORY_MB=7000
      - CLIENT_ID=${CLIENT_ID}
    ports:
      - "8081:8081"
      - "29344:29344"
    volumes:
      - ./data:/app/data
      - /var/run/dstack.sock:/var/run/dstack.sock
    restart: always
```

---

## TDX Quote Integration

### Enhanced Attestation Client
```python
# src/shared/dstack_attestation.py
import requests

class DstackAttestationClient:
    def __init__(self, socket_path="/var/run/dstack.sock"):
        self.socket_path = socket_path
    
    async def get_tdx_quote(self, report_data: str) -> Dict:
        \"\"\"Get TDX quote from dstack guest agent\"\"\"
        response = requests.get(
            f"http://localhost/GetQuote?report_data={report_data}",
            unix_socket=self.socket_path
        )
        return response.json()
    
    async def generate_agent_attestation(self, agent_id: str, public_key: str) -> Dict:
        \"\"\"Generate attestation with dstack TDX quote\"\"\"
        agent_data = {
            "agent_id": agent_id,
            "public_key": public_key,
            "timestamp": int(time.time())
        }
        
        report_data_hex = "0x" + json.dumps(agent_data, sort_keys=True).encode().hex()
        quote_response = await self.get_tdx_quote(report_data_hex)
        
        return {
            "agent_data": agent_data,
            "tdx_quote": quote_response,
            "verification_status": "pending"
        }
```

---

## Deployment Process

### 1. Start dstack Services
```bash
# Terminal 1: KMS
./dstack-kms -c kms.toml

# Terminal 2: Gateway
sudo ./dstack-gateway -c gateway.toml

# Terminal 3: VMM
./dstack-vmm -c vmm.toml
```

### 2. Deploy via Web Interface
1. Access dstack-vmm at `http://localhost:9080`
2. Upload `hub-dstack-compose.yaml`
3. Upload agent compose files as needed
4. Monitor deployment via dstack dashboard

### 3. Access Patterns
```
# Hub access
https://hub-${CLIENT_ID}.boardroom-tee.domain.com

# Agent access
https://finance-${CLIENT_ID}.boardroom-tee.domain.com
https://marketing-${CLIENT_ID}.boardroom-tee.domain.com
```

---

## Zero Trust HTTPS Setup

### Automated Certificate Management
```bash
# Configure Cloudflare integration
CF_ZONE_ID=your_zone_id
CF_API_TOKEN=your_api_token
BASE_DOMAIN=boardroom-tee.your-domain.com

# Launch certbot for automated TLS
RUST_LOG=info,certbot=debug ./certbot renew -c certbot.toml
```

### Certificate Monitoring
```bash
# Monitor certificate transparency
./ct_monitor -t https://localhost:9010/prpc -d boardroom-tee.your-domain.com
```

---

## Comparison: dstack vs Direct Docker

### Use dstack for:
- **Production deployments** requiring hardware attestation
- **Enterprise clients** needing certificate transparency
- **Regulatory compliance** requiring verifiable TEE execution
- **Zero-trust environments** with automated certificate management

### Use Direct Docker for:
- **Development and testing** environments
- **Quick prototyping** and iteration
- **Cost-sensitive deployments** where TEE guarantees aren't required
- **Custom security requirements** needing specialized configurations

---

*Last Updated: December 2024*  
*Related: [`03-deployment/docker-deployment.md`](./docker-deployment.md) for direct Docker approach*  
*Purpose: Alternative TEE deployment option for Claude implementation*