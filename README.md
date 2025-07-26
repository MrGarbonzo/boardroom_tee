# Boardroom TEE

> **Secure Multi-Agent AI Platform for Enterprise Business Intelligence**

Boardroom TEE is a hub-and-spoke AI system that provides privacy-first access to ALL company data through specialized departmental agents running in Trusted Execution Environments (TEE). Get multi-specialist business intelligence with hardware-guaranteed security.

## 🚀 Quick Deploy

**Deploy distributed system across multiple VMs:**

### Step 1: Deploy Hub VM
```bash
# On Hub VM
wget https://raw.githubusercontent.com/[your-org]/boardroom-tee/main/hub/docker-compose.yaml
export CLIENT_ID=your-company-name
docker-compose up -d
# Note the Hub VM IP address
```

### Step 2: Deploy Finance VM
```bash
# On Finance VM
wget https://raw.githubusercontent.com/[your-org]/boardroom-tee/main/spoke_finance/docker-compose.yaml
wget https://raw.githubusercontent.com/[your-org]/boardroom-tee/main/spoke_finance/.env.example
# Edit .env with Hub IP address
echo "HUB_ENDPOINT=http://[HUB_IP]:8080" > .env
docker-compose up -d
```

### Step 3: Deploy Marketing VM
```bash
# On Marketing VM
wget https://raw.githubusercontent.com/[your-org]/boardroom-tee/main/spoke_marketing/docker-compose.yaml
wget https://raw.githubusercontent.com/[your-org]/boardroom-tee/main/spoke_marketing/.env.example
# Edit .env with Hub IP address
echo "HUB_ENDPOINT=http://[HUB_IP]:8080" > .env
docker-compose up -d
```

### Step 4: Update Hub with Spoke IPs
```bash
# On Hub VM - update .env with all spoke IPs
echo "FINANCE_ENDPOINT=http://[FINANCE_IP]:8081" >> .env
echo "MARKETING_ENDPOINT=http://[MARKETING_IP]:8082" >> .env
docker-compose restart
```

**Each component runs on its own VM with complete isolation!**

## 🏗️ Architecture

### Core Innovation: Agent-to-Agent Collaboration
Dynamic multi-specialist analysis without fixed pipeline overhead. Agents collaborate on-demand through secure attestation-verified communication.

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Hub VM        │◄──►│ Finance VM      │◄──►│ Marketing VM    │
│ Llama-3.2-1B    │    │ AdaptLLM/7B     │    │ Mistral-7B      │
│ [HUB_IP]:8080   │    │ [FIN_IP]:8081   │    │ [MKT_IP]:8082   │
│ GHCR: hub       │    │ GHCR: finance   │    │ GHCR: marketing │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         ▲                       ▲                       ▲
         │                       │                       │
    ┌─────────────────────────────────────────────────────────┐
    │         Cross-VM TEE Communication                     │
    │      Manual IP Configuration via .env Files           │
    └─────────────────────────────────────────────────────────┘
```

### MVP Components (Phase 1)
- **Hub**: Data organization + agent orchestration (Llama-3.2-1B-Instruct)
- **Finance Agent**: Specialized financial analysis (AdaptLLM/Finance-LLM-7B)
- **Marketing Agent**: Marketing intelligence (Mistral-7B-Instruct-v0.3)
- **Web UI**: Simple document upload and query interface

## 🎯 Value Proposition

### For Businesses
- **Complete Infrastructure Isolation**: Your dedicated VMs never share resources with competitors
- **Hardware-Guaranteed Security**: Each client gets dedicated TEE-protected infrastructure
- **Independent Verification**: Verify our TEE deployment integrity via port 29343 attestation endpoint
- **Verifiable AI Provenance**: Every response cryptographically signed with proof of TEE origin
- **Multi-Specialist Intelligence**: Finance + Marketing + Sales agents collaborate like a real boardroom
- **Complete Data Access**: Upload ALL company data - financial reports, marketing campaigns, sales pipelines
- **Cryptographic Audit Trail**: Complete verifiable record of all AI-generated insights
- **Zero Trust Verification**: Clients can independently verify deployment using reproduce-mr tools

### For Developers
- **Pre-Built Images**: No compilation needed - deploy from GitHub Container Registry
- **SecretVM TEE Security**: Hardware-guaranteed security with independent attestation verification
- **Modular Architecture**: Add new agents without touching existing code
- **API-First**: Complete REST APIs for all components
- **Reproducible Builds**: Clients can independently verify deployment integrity

## 📋 System Requirements

### Per Client Infrastructure Requirements
**Each business client gets dedicated VMs:**

**Hub VM (Per Client):**
- **CPU**: 2 vCPU (with TEE support - Intel TDX or AMD SEV)
- **Memory**: 4GB RAM
- **Storage**: 50GB SSD
- **Network**: Public IPv4 address

**Finance Agent VM (Per Client):**
- **CPU**: 2 vCPU (with TEE support)
- **Memory**: 8GB RAM
- **Storage**: 40GB SSD
- **Network**: Public IPv4 address

**Marketing Agent VM (Per Client):**
- **CPU**: 2 vCPU (with TEE support)
- **Memory**: 8GB RAM
- **Storage**: 40GB SSD
- **Network**: Public IPv4 address

**Total Per Client**: 3 dedicated VMs, 6 vCPU, 20GB RAM, 130GB storage

### Software Dependencies
- **OS**: Ubuntu 22.04+ with Intel TDX support
- **TEE Platform**: SecretVM with attestation verification
- **Docker**: Docker Engine 24.0+ with SecretVM integration
- **Network**: Ports 8080-8082 (APIs), 29343-29345 (attestation endpoints)
- **Verification**: Port 29343 endpoint for client attestation verification

## 🚀 Deployment Options

### Option 1: Manual VM Deploy (Recommended)
```bash
# Deploy each component to separate VMs following Quick Deploy steps above
# Allows complete control over VM placement and networking
```

### Option 2: Cloud VM Templates
- **AWS**: Use our CloudFormation template for multi-VM deployment
- **Azure**: ARM template for Confidential Computing VMs
- **GCP**: Deployment Manager template with TEE support
- **dstack**: Multi-VM TEE deployment configuration

### Option 3: Infrastructure as Code
```bash
# Terraform deployment
terraform apply -var="client_id=your-company"
# Automatically provisions all VMs and configures IP addresses
```

## 📊 Service Endpoints

After deployment, access these endpoints:

| Service | URL | Purpose |
|---------|-----|---------|
| **Hub API** | `http://[HUB_IP]:8080` | Document upload, agent orchestration |
| **Finance Agent** | `http://[FINANCE_IP]:8081` | Financial analysis and calculations |
| **Marketing Agent** | `http://[MARKETING_IP]:8082` | Marketing intelligence and campaigns |
| **Web Interface** | `http://[HUB_IP]:3000` | Simple upload/query UI |
| **Health Dashboard** | `http://[HUB_IP]:8080/health` | System status monitoring |

## 💡 Demo Workflow

**Try this example after deployment:**

1. **Upload Data**: Upload your Q4 marketing campaign report
2. **Ask Question**: "What was the ROI on our holiday marketing campaign?"
3. **Watch Collaboration**:
   - Marketing Agent analyzes campaign performance
   - Finance Agent calculates ROI with marketing context
   - Hub synthesizes complete analysis
4. **Get Results**: Comprehensive financial analysis with marketing insights

## 🔧 Management Commands

```bash
# Check system health (run on each VM)
curl http://[HUB_IP]:8080/health
curl http://[FINANCE_IP]:8081/health
curl http://[MARKETING_IP]:8082/health

# View logs (on respective VMs)
# On Hub VM:
docker-compose logs
# On Finance VM:
docker-compose logs
# On Marketing VM:
docker-compose logs

# Stop services (on each VM individually)
docker-compose down

# Update to latest images (on each VM)
docker-compose pull && docker-compose up -d
```

## 🏢 Pricing Tiers

| Tier | Components | Use Case | Monthly Cost |
|------|------------|----------|--------------|
| **Basic** | Hub + Finance | Financial analysis | $299/month |
| **Premium** | Hub + Finance + Marketing + Sales | Multi-department insights | $599/month |
| **Enterprise** | All Agents + CEO Agent | Complete business intelligence | $999/month |

## 🔒 Security Model

### TEE Protection
- **Hardware Attestation**: All agents run in Intel TDX SecretVM enclaves
- **Independent Verification**: Clients can verify TEE integrity via port 29343 attestation endpoints
- **Verifiable Message Signing**: Every cross-VM message cryptographically signed with ed25519
- **Cryptographic Provenance**: Cryptographic proof that responses originated from verified TEE-protected AI agents
- **Complete Infrastructure Isolation**: Each client gets dedicated VMs with zero shared resources
- **Dedicated TEE Keys**: Unique cryptographic identity per client with no key sharing
- **Reproducible Builds**: Clients can independently verify our deployment using reproduce-mr tools
- **Zero Knowledge**: We cannot access your data even if we wanted to

### Trust Boundaries
- ✅ **Trusted**: TEE hardware, VMS-signed messages, verified agents, encrypted data
- ❌ **Untrusted**: Host OS, network, unsigned messages, unverified agents
- 🔐 **Verification**: Hardware attestation + VMS cryptographic proof + weekly key rotation

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| **[Quick Start](./docs/00-INDEX.md)** | Implementation guide for developers |
| **[Architecture](./docs/01-architecture/)** | System design and component details |
| **[API Reference](./docs/04-apis/)** | Complete REST API documentation |
| **[Deployment](./docs/03-deployment/)** | Docker and infrastructure setup |
| **[Security](./docs/05-security/)** | TEE implementation and attestation |

## 🛠️ Development

### For Contributors
```bash
# Clone repository
git clone https://github.com/[your-org]/boardroom-tee.git
cd boardroom-tee

# Development setup
cp .env.example .env
docker-compose -f docker-compose.dev.yaml up -d

# See CONTRIBUTING.md for detailed development guide
```

### GitHub Actions
- **Build**: Automatic image building on every commit
- **Test**: Comprehensive testing across all components  
- **Deploy**: Automatic deployment to GitHub Container Registry
- **Security**: Automated security scanning and attestation verification

## 🌟 Key Features

### Agent Collaboration
- **Dynamic Routing**: Hub intelligently routes queries to best agents
- **Cross-Domain Analysis**: Finance + Marketing collaboration for ROI analysis
- **Attestation-Verified**: All agent communication cryptographically verified
- **Cost Tracking**: Monitor collaboration costs across departments

### Data Processing
- **Universal Upload**: PDF, DOCX, Excel, CSV, Email support
- **Smart Categorization**: LLM-powered document organization
- **Secure Storage**: All data encrypted within TEE boundaries
- **Instant Access**: Agents can access relevant data in milliseconds

### Enterprise Ready
- **Multi-Tenant**: Complete client isolation
- **Scalable**: Horizontal scaling of individual agents
- **Monitored**: Comprehensive logging and health monitoring
- **Compliant**: SOC 2, GDPR, HIPAA compatible architecture

## 🚧 Roadmap

### Phase 1: MVP (Current)
- ✅ Hub + Finance + Marketing agents
- ✅ Basic collaboration workflows
- ✅ TEE security implementation
- ✅ Simple web interface

### Phase 2: Expansion (Q2 2025)
- 🔄 Sales Agent integration
- 🔄 Advanced collaboration patterns
- 🔄 Enhanced web interface
- 🔄 Performance optimization

### Phase 3: Enterprise (Q3 2025)
- 📋 CEO Agent with strategic synthesis
- 📋 Advanced analytics dashboard
- 📋 Enterprise integrations (Salesforce, HubSpot)
- 📋 Multi-cloud deployment

## 🤝 Support

- **Documentation**: [Full documentation](./docs/)
- **Issues**: [GitHub Issues](https://github.com/[your-org]/boardroom-tee/issues)
- **Discussions**: [GitHub Discussions](https://github.com/[your-org]/boardroom-tee/discussions)
- **Enterprise Support**: enterprise@boardroom-tee.com

## 📄 License

MIT License - see [LICENSE](./LICENSE) for details.

---

**Ready to transform your business intelligence with secure multi-agent AI?**

[![Deploy to Cloud](https://img.shields.io/badge/Deploy-Cloud%20VM-blue?style=for-the-badge)](./docs/03-deployment/)
[![View Docs](https://img.shields.io/badge/View-Documentation-green?style=for-the-badge)](./docs/)
[![GitHub](https://img.shields.io/badge/GitHub-Repository-black?style=for-the-badge)](https://github.com/[your-org]/boardroom-tee)

*Boardroom TEE: Where AI meets enterprise security* 🚀