# Docker Deployment Guide - Boardroom TEE

## Overview
Complete Docker deployment guide for Boardroom TEE hub-and-spoke architecture with TEE security integration.

---

## Prerequisites

### System Requirements
- **TEE Environment**: SecretVM or compatible TEE platform
- **Hardware**: Minimum 16GB RAM, 100GB storage per client deployment
- **Network**: Public IPv4 address, domain access for HTTPS
- **Docker**: Docker Engine 20.10+ with TEE integration

### Software Dependencies
```bash
# Ubuntu 24.04 LTS
sudo apt update && sudo apt install -y \\
    docker.io docker-compose-plugin \\
    curl wget git build-essential \\
    python3 python3-pip

# Verify TEE support
sudo dmesg | grep -i tdx
```

---

## Environment Setup

### 1. Create Client Environment
```bash
# Create client-specific environment file
cat > .env << EOF
CLIENT_ID=client-unique-identifier
HUB_ENDPOINT=https://hub-${CLIENT_ID}.boardroom-tee.com:8080
HUB_ATTESTATION_ENDPOINT=https://hub-${CLIENT_ID}.boardroom-tee.com:29343

# Resource limits
HUB_MEMORY_LIMIT=4G
FINANCE_MEMORY_LIMIT=8G
MARKETING_MEMORY_LIMIT=8G
SALES_MEMORY_LIMIT=8G
CEO_MEMORY_LIMIT=12G

# Logging
LOG_LEVEL=INFO
AUDIT_ENABLED=true
EOF
```

### 2. Create Docker Network
```bash
# Shared network for component communication
docker network create boardroom-network --driver bridge
```

### 3. Directory Structure Setup
```bash
# Create deployment structure
mkdir -p boardroom-tee-${CLIENT_ID}
cd boardroom-tee-${CLIENT_ID}

# Component directories
mkdir -p {hub,spoke_finance,spoke_marketing,spoke_sales,spoke_ceo}/{data,logs,config,crypto}

# Shared configurations
mkdir -p shared/{certs,backup}
```

---

## Component Deployment

### Hub Deployment (Deploy First)

```yaml
# hub/docker-compose.yaml
version: '3.8'

services:
  boardroom-hub:
    image: hub-boardroom-tee:latest
    container_name: boardroom-hub-${CLIENT_ID}
    
    environment:
      - HUB_MODEL_NAME=meta-llama/Llama-3.2-1B-Instruct
      - HUB_MAX_MEMORY_MB=3000
      - HUB_API_PORT=8080
      - HUB_ATTESTATION_PORT=29343
      - CLIENT_ID=${CLIENT_ID}
      - LOG_LEVEL=${LOG_LEVEL}
      - AUDIT_ENABLED=${PRESENT_ENABLED}
    
    ports:
      - \"8080:8080\"
      - \"29343:29343\"
    
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
      - ./config:/app/config
      - ./crypto:/app/crypto
      - /dev/sgx_enclave:/dev/sgx_enclave  # TEE device access
      - /dev/sgx_provision:/dev/sgx_provision
    
    networks:
      - boardroom-network
    
    restart: unless-stopped
    
    deploy:
      resources:
        limits:
          memory: ${HUB_MEMORY_LIMIT}
          cpus: '2'
        reservations:
          memory: 2G
          cpus: '1'
    
    healthcheck:
      test: [\"CMD\", \"curl\", \"-f\", \"http://localhost:8080/health\"]
      interval: 30s
      timeout: 10s
      retries: 3

networks:
  boardroom-network:
    external: true
```

### Finance Agent Deployment

```yaml
# spoke_finance/docker-compose.yaml
version: '3.8'

services:
  finance-agent:
    image: finance-boardroom-tee:latest
    container_name: finance-agent-${CLIENT_ID}
    
    environment:
      - AGENT_TYPE=finance
      - AGENT_MODEL_NAME=AdaptLLM/finance-LLM
      - AGENT_API_PORT=8081
      - AGENT_ATTESTATION_PORT=29344
      - AGENT_MAX_MEMORY_MB=7000
      - CLIENT_ID=${CLIENT_ID}
      - HUB_ENDPOINT=${HUB_ENDPOINT}
      - HUB_ATTESTATION_ENDPOINT=${HUB_ATTESTATION_ENDPOINT}
      - LOG_LEVEL=${LOG_LEVEL}
    
    ports:
      - \"8081:8081\"
      - \"29344:29344\"
    
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
      - ./config:/app/config
      - ./crypto:/app/crypto
      - /dev/sgx_enclave:/dev/sgx_enclave
      - /dev/sgx_provision:/dev/sgx_provision
    
    networks:
      - boardroom-network
    
    depends_on:
      - boardroom-hub
    
    restart: unless-stopped
    
    deploy:
      resources:
        limits:
          memory: ${FINANCE_MEMORY_LIMIT}
          cpus: '2'

networks:
  boardroom-network:
    external: true
```

### Marketing Agent Deployment

```yaml
# spoke_marketing/docker-compose.yaml
version: '3.8'

services:
  marketing-agent:
    image: marketing-boardroom-tee:latest
    container_name: marketing-agent-${CLIENT_ID}
    
    environment:
      - AGENT_TYPE=marketing
      - AGENT_MODEL_NAME=mistralai/Mistral-7B-Instruct-v0.3
      - AGENT_API_PORT=8082
      - AGENT_ATTESTATION_PORT=29345
      - AGENT_MAX_MEMORY_MB=7000
      - CLIENT_ID=${CLIENT_ID}
      - HUB_ENDPOINT=${HUB_ENDPOINT}
      - HUB_ATTESTATION_ENDPOINT=${HUB_ATTESTATION_ENDPOINT}
    
    ports:
      - \"8082:8082\"
      - \"29345:29345\"
    
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
      - ./config:/app/config
      - ./crypto:/app/crypto
      - /dev/sgx_enclave:/dev/sgx_enclave
      - /dev/sgx_provision:/dev/sgx_provision
    
    networks:
      - boardroom-network
    
    depends_on:
      - boardroom-hub
    
    deploy:
      resources:
        limits:
          memory: ${MARKETING_MEMORY_LIMIT}
          cpus: '2'

networks:
  boardroom-network:
    external: true
```

---

## Build Process

### Build Script
```bash
#!/bin/bash
# build.sh

set -e

CLIENT_ID=${1:-\"demo-client\"}
echo \"Building Boardroom TEE for client: $CLIENT_ID\"

echo \"Building base agent framework...\"
docker build -t boardroom-base-agent:latest -f base-agent/Dockerfile .

echo \"Building hub container...\"
docker build -t hub-boardroom-tee:latest -f hub/Dockerfile .

echo \"Building finance agent...\"
docker build -t finance-boardroom-tee:latest -f spoke_finance/Dockerfile .

echo \"Building marketing agent...\"
docker build -t marketing-boardroom-tee:latest -f spoke_marketing/Dockerfile .

echo \"Building sales agent...\"
docker build -t sales-boardroom-tee:latest -f spoke_sales/Dockerfile .

echo \"Building CEO agent...\"
docker build -t ceo-boardroom-tee:latest -f spoke_ceo/Dockerfile .

echo \"All images built successfully!\"
docker images | grep boardroom
```

### Deployment Script
```bash
#!/bin/bash
# deploy.sh

CLIENT_ID=${1:-\"demo-client\"}
TIER=${2:-\"premium\"}  # basic, premium, enterprise

echo \"Deploying Boardroom TEE for client: $CLIENT_ID (tier: $TIER)\"

# Set environment
export CLIENT_ID=$CLIENT_ID

# Deploy hub (always required)
echo \"Deploying hub...\"
cd hub && docker-compose up -d && cd ..

# Deploy agents based on tier
case $TIER in
    \"basic\")
        echo \"Deploying basic tier: hub + finance\"
        cd spoke_finance && docker-compose up -d && cd ..
        ;;
    \"premium\")
        echo \"Deploying premium tier: hub + finance + marketing + sales\"
        cd spoke_finance && docker-compose up -d && cd ..
        cd spoke_marketing && docker-compose up -d && cd ..
        cd spoke_sales && docker-compose up -d && cd ..
        ;;
    \"enterprise\")
        echo \"Deploying enterprise tier: all agents\"
        cd spoke_finance && docker-compose up -d && cd ..
        cd spoke_marketing && docker-compose up -d && cd ..
        cd spoke_sales && docker-compose up -d && cd ..
        cd spoke_ceo && docker-compose up -d && cd ..
        ;;
esac

echo \"Deployment complete for $CLIENT_ID ($TIER tier)\"
```

---

## Service Management

### Health Monitoring
```bash
#!/bin/bash
# health-check.sh

CLIENT_ID=${1:-\"demo-client\"}

echo \"Health check for client: $CLIENT_ID\"

# Check hub
echo \"Hub status:\"
curl -s http://localhost:8080/health | jq .

# Check finance agent
echo \"Finance agent status:\"
curl -s http://localhost:8081/health | jq .

# Check marketing agent
echo \"Marketing agent status:\"
curl -s http://localhost:8082/health | jq .

# Container status
echo \"Container status:\"
docker ps --filter name=\"$CLIENT_ID\" --format \"table {{.Names}}\\t{{.Status}}\\t{{.Ports}}\"
```

### Log Management
```bash
#!/bin/bash
# logs.sh

CLIENT_ID=${1:-\"demo-client\"}
COMPONENT=${2:-\"all\"}

case $COMPONENT in
    \"hub\")
        docker logs -f boardroom-hub-$CLIENT_ID
        ;;
    \"finance\")
        docker logs -f finance-agent-$CLIENT_ID
        ;;
    \"marketing\")
        docker logs -f marketing-agent-$CLIENT_ID
        ;;
    \"all\")
        docker logs -f boardroom-hub-$CLIENT_ID &
        docker logs -f finance-agent-$CLIENT_ID &
        docker logs -f marketing-agent-$CLIENT_ID &
        wait
        ;;
esac
```

### Resource Monitoring
```bash
#!/bin/bash
# monitor.sh

CLIENT_ID=${1:-\"demo-client\"}

echo \"Resource usage for client: $CLIENT_ID\"

# Container stats
docker stats --format \"table {{.Container}}\\t{{.CPUPerc}}\\t{{.MemUsage}}\\t{{.NetIO}}\" \\
    --filter name=\"$CLIENT_ID\"

# Disk usage
echo \"\\nStorage usage:\"
du -sh */data

# Memory usage by model
echo \"\\nModel memory usage:\"
curl -s http://localhost:8080/health | jq '.memory_usage'
curl -s http://localhost:8081/health | jq '.memory_usage'
curl -s http://localhost:8082/health | jq '.memory_usage'
```

---

## Scaling & Updates

### Horizontal Scaling
```bash
# Scale specific agent for high load
docker-compose -f spoke_finance/docker-compose.yaml up --scale finance-agent=3

# Load balancer configuration for multiple instances
# (requires nginx or similar load balancer setup)
```

### Rolling Updates
```bash
#!/bin/bash
# update.sh

COMPONENT=${1:-\"hub\"}
CLIENT_ID=${2:-\"demo-client\"}

echo \"Updating $COMPONENT for client $CLIENT_ID\"

cd $COMPONENT

# Pull latest image
docker-compose pull

# Rolling update with zero downtime
docker-compose up -d --no-deps $COMPONENT

# Verify health
sleep 30
curl -f http://localhost:808X/health || echo \"Health check failed\"

echo \"Update complete for $COMPONENT\"
```

---

## Security Configuration

### TEE Device Access
```yaml
# Required device mounts for TEE functionality
volumes:
  - /dev/sgx_enclave:/dev/sgx_enclave
  - /dev/sgx_provision:/dev/sgx_provision
  - /var/run/aesmd:/var/run/aesmd

# Security options
security_opt:
  - no-new-privileges:true
  - seccomp:unconfined  # Required for TEE operations

# Privileged mode for TEE access
privileged: false  # Use specific device access instead
```

### Network Security
```yaml
# Network isolation
networks:
  boardroom-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16
    driver_opts:
      com.docker.network.bridge.enable_icc: \"true\"
      com.docker.network.bridge.enable_ip_masquerade: \"true\"
```

---

## Troubleshooting

### Common Issues

#### TEE Device Access
```bash
# Check TEE device availability
ls -la /dev/sgx_*
sudo dmesg | grep -i sgx

# Fix permissions
sudo chmod 666 /dev/sgx_enclave
sudo chmod 666 /dev/sgx_provision
```

#### Memory Issues
```bash
# Check available memory
free -h

# Optimize Docker memory
docker system prune -f
docker volume prune -f

# Adjust memory limits in docker-compose.yaml
```

#### Network Connectivity
```bash
# Test inter-container communication
docker exec boardroom-hub-$CLIENT_ID ping finance-agent-$CLIENT_ID

# Check port availability
netstat -tlnp | grep :808[0-4]
```

---

*Last Updated: December 2024*  
*Related: [`03-deployment/dstack-deployment.md`](./dstack-deployment.md) for alternative TEE deployment*  
*Purpose: Complete Docker deployment guide for Claude implementation*