# Boardroom TEE - Deployment Structure

## Overview
Modular deployment architecture where each component can be deployed independently with a single docker-compose command.

---

## Directory Structure
```
F:/coding/boardroom_tee/
├── hub/                           # Central data hub
│   ├── docker-compose.yaml       # Hub deployment
│   ├── README.md                  # Hub documentation
│   ├── data/                      # Data persistence
│   ├── logs/                      # Audit logs
│   └── config/                    # Configuration
│
├── spoke_finance/                 # Finance analysis agent
│   ├── docker-compose.yaml       # Finance agent deployment
│   ├── README.md                  # Finance agent documentation
│   ├── data/                      # Agent data
│   ├── logs/                      # Agent logs
│   └── config/                    # Agent configuration
│
├── spoke_marketing/               # Marketing analysis agent
│   ├── docker-compose.yaml       # Marketing agent deployment
│   ├── README.md                  # Marketing agent documentation
│   ├── data/                      # Agent data
│   ├── logs/                      # Agent logs
│   └── config/                    # Agent configuration
│
├── spoke_sales/                   # Sales pipeline agent
│   ├── docker-compose.yaml       # Sales agent deployment
│   ├── README.md                  # Sales agent documentation
│   ├── data/                      # Agent data
│   ├── logs/                      # Agent logs
│   └── config/                    # Agent configuration
│
├── spoke_ceo/                     # CEO strategic agent (premium)
│   ├── docker-compose.yaml       # CEO agent deployment
│   ├── README.md                  # CEO agent documentation
│   ├── data/                      # Agent data
│   ├── logs/                      # Agent logs
│   └── config/                    # Agent configuration
│
├── resources/                     # Technical documentation
└── boardroom_tee_planning.md      # Main planning document
```

---

## Deployment Process

### 1. Environment Setup
```bash
# Create shared environment variables
cat > .env << EOF
CLIENT_ID=client-unique-identifier
HUB_ENDPOINT=https://hub-domain:8080
HUB_ATTESTATION_ENDPOINT=https://hub-domain:29343
EOF
```

### 2. Network Creation
```bash
# Create shared network for agent communication
docker network create boardroom-network
```

### 3. Hub Deployment (Deploy First)
```bash
cd F:/coding/boardroom_tee/hub
docker-compose up -d
```

### 4. Spoke Agent Deployment (Any Order)
```bash
# Finance Agent
cd F:/coding/boardroom_tee/spoke_finance
docker-compose up -d

# Marketing Agent
cd F:/coding/boardroom_tee/spoke_marketing
docker-compose up -d

# Sales Agent
cd F:/coding/boardroom_tee/spoke_sales
docker-compose up -d

# CEO Agent (Premium Tier)
cd F:/coding/boardroom_tee/spoke_ceo
docker-compose up -d
```

---

## Service Architecture

### Port Allocation
- **Hub**: 8080 (API), 29343 (Attestation)
- **Finance Agent**: 8081 (API), 29344 (Attestation)
- **Marketing Agent**: 8082 (API), 29345 (Attestation)
- **Sales Agent**: 8083 (API), 29346 (Attestation)
- **CEO Agent**: 8084 (API), 29347 (Attestation)

### Resource Requirements
- **Hub**: Medium (2 vCPU, 4GB RAM, Expanded Storage)
- **Finance Agent**: Medium (2 vCPU, 4GB RAM, 40GB Storage)
- **Marketing Agent**: Small (1 vCPU, 2GB RAM, 20GB Storage)
- **Sales Agent**: Small (1 vCPU, 2GB RAM, 20GB Storage)
- **CEO Agent**: Large (4 vCPU, 8GB RAM, 80GB Storage)

### Security Features
- **TEE Environment**: All components run in SecretVM TEE
- **Verifiable Message Signing**: Automatic key generation per component
- **Attestation Verification**: Hub verifies all agent communications
- **Data Isolation**: Complete client data separation per deployment

---

## Scaling Strategy

### Basic Tier Deployment
```bash
# Minimal deployment for cost-conscious clients
docker-compose up -d hub
docker-compose up -d spoke_finance
docker-compose up -d marketing
```

### Premium Tier Deployment
```bash
# Full deployment with agent collaboration
docker-compose up -d hub
docker-compose up -d spoke_finance
docker-compose up -d marketing
docker-compose up -d sales
docker-compose up -d ceo
```

### Multi-Client Deployment
- Each client gets dedicated VM instances
- Separate deployments with unique CLIENT_ID
- Complete data isolation between clients
- Independent scaling per client needs

---

## Management Commands

### Health Checks
```bash
# Check all services
curl http://hub:8080/health
curl http://finance-agent:8081/health
curl http://marketing-agent:8082/health
curl http://sales-agent:8083/health
curl http://ceo-agent:8084/health
```

### Monitoring
```bash
# View logs
docker-compose logs -f boardroom-hub
docker-compose logs -f boardroom-finance-agent

# Resource usage
docker stats
```

### Updates
```bash
# Update individual components
cd F:/coding/boardroom_tee/spoke_finance
docker-compose pull
docker-compose up -d
```

---

## Configuration Management

### Environment Variables
- `CLIENT_ID`: Unique client identifier for data isolation
- `HUB_ENDPOINT`: Hub API endpoint for agent registration
- `HUB_ATTESTATION_ENDPOINT`: Hub attestation verification endpoint
- `AGENT_LOG_LEVEL`: Logging verbosity (DEBUG, INFO, WARN, ERROR)

### Volume Mounts
- `./data`: Persistent data storage
- `./logs`: Audit and application logs
- `./config`: Component configuration files
- `./crypto`: SecretVM generated keys (auto-mounted)

### Network Configuration
- **boardroom-network**: Shared bridge network for component communication
- **External connectivity**: Hub exposes public API, agents communicate internally
- **Security**: All inter-component communication verified via attestation

---

This modular structure enables:
- **Independent deployment** of each component
- **Flexible scaling** based on client needs and pricing tiers
- **Easy maintenance** and updates per component
- **Complete isolation** between different client deployments
- **Cost optimization** by deploying only needed agents

*Last Updated: [Current Date]*
