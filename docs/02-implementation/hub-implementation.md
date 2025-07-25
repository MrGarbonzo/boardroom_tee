# Hub Implementation - Central Data Repository & Orchestration

## Overview
The hub serves as the central data repository, document processor, and agent orchestration layer. It manages data ingestion, TinyLlama-based organization, and secure distribution to spoke agents.

---

## Core Components

### 1. Unified LLM Manager (Llama-3.2-1B-Instruct)
**Purpose**: Single model handling both data organization AND agent orchestration

**Architecture Decision**: Use one model for dual purposes instead of separate models
- **Data Processing**: Document categorization, keyword extraction, metadata generation
- **Agent Orchestration**: Capability matching, routing decisions, collaboration coordination

```python
# src/hub/services/unified_hub_llm.py
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from typing import Dict, List, Optional, Tuple

class UnifiedHubLLM:
    \"\"\"Unified LLM for both data processing and agent orchestration\"\"\"
    
    def __init__(self, model_name: str = \"meta-llama/Llama-3.2-1B-Instruct\"):
        self.model_name = model_name
        self.model = None
        self.tokenizer = None
        self.is_loaded = False
        
    async def load_model(self) -> bool:
        \"\"\"Load Llama-3.2-1B-Instruct for dual usage\"\"\"
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                torch_dtype=torch.float16,
                device_map=\"cpu\",
                low_cpu_mem_usage=True
            )
            
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
                
            self.is_loaded = True
            return True
        except Exception as e:
            logging.error(f\"Failed to load hub model: {e}\")
            return False
    
    def categorize_document(self, text_content: str) -> Dict:
        \"\"\"Categorize uploaded document content\"\"\"
        prompt = f\"\"\"Analyze this business document and categorize it:

Document Content:
{text_content[:2000]}...

Provide categorization in this format:
Department: [Finance/Marketing/Sales/Operations/Other]
Document Type: [Report/Data/Email/Planning/Contract]
Key Terms: [5-10 keywords]
Time Period: [Any dates mentioned]
Summary: [Brief description]
\"\"\"
        
        response = self._generate_response(prompt)
        return self._parse_categorization(response)
    
    def route_agent_request(self, query: str, available_agents: List[Dict]) -> Dict:
        \"\"\"Route collaboration request to best agent\"\"\"
        agent_list = \"\\n\".join([
            f\"- {agent['agent_type']}: {', '.join(agent['capabilities'])}\"
            for agent in available_agents
        ])
        
        prompt = f\"\"\"Route this business query to the best agent:

Query: {query}

Available Agents:
{agent_list}

Respond with:
Best Agent: [agent_type]
Reasoning: [why this agent is best]
Priority: [high/medium/low]
Estimated Time: [minutes]
\"\"\"
        
        response = self._generate_response(prompt)
        return self._parse_routing_decision(response)
    
    def synthesize_collaboration_results(self, results: List[Dict]) -> Dict:
        \"\"\"Synthesize results from multiple agent collaboration\"\"\"
        results_summary = \"\\n\".join([
            f\"Agent {r['agent_type']}: {r['summary']}\"
            for r in results
        ])
        
        prompt = f\"\"\"Synthesize these specialist analyses into executive summary:

Specialist Results:
{results_summary}

Provide:
Executive Summary: [key findings]
Recommendations: [actionable items]
Confidence Score: [0.0-1.0]
Areas of Agreement: [where specialists agree]
Areas of Disagreement: [conflicts to resolve]
\"\"\"
        
        response = self._generate_response(prompt)
        return self._parse_synthesis_result(response)
    
    def _generate_response(self, prompt: str) -> str:
        \"\"\"Generate response using Llama-3.2-1B\"\"\"
        inputs = self.tokenizer(prompt, return_tensors=\"pt\", truncation=True, max_length=1024)
        
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=512,
                temperature=0.7,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id
            )
        
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return response[len(prompt):].strip()
```

### 2. Document Processing Pipeline

```python
# src/hub/services/document_processor.py
import PyPDF2
import pandas as pd
from docx import Document
import email
from typing import Dict, Optional

class DocumentProcessor:
    \"\"\"Document content extraction and processing\"\"\"
    
    def __init__(self, hub_llm: UnifiedHubLLM):
        self.hub_llm = hub_llm
        
    async def process_upload(self, file_path: str, filename: str, metadata: Dict) -> Dict:
        \"\"\"Process uploaded document\"\"\"
        try:
            # Extract text content
            text_content = self._extract_text_content(file_path, filename)
            
            # Categorize using LLM
            categorization = self.hub_llm.categorize_document(text_content)
            
            # Generate metadata
            document_metadata = {
                \"filename\": filename,
                \"upload_date\": datetime.utcnow().isoformat(),
                \"file_size\": os.path.getsize(file_path),
                \"file_type\": self._detect_file_type(filename),
                \"categorization\": categorization,
                \"user_metadata\": metadata
            }
            
            # Store processed content
            document_id = self._store_processed_document(text_content, document_metadata)
            
            return {
                \"document_id\": document_id,
                \"status\": \"processed\",
                \"categorization\": categorization,
                \"processing_time\": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                \"status\": \"failed\",
                \"error\": str(e),
                \"processing_time\": datetime.utcnow().isoformat()
            }
    
    def _extract_text_content(self, file_path: str, filename: str) -> str:
        \"\"\"Extract plain text from various file types\"\"\"
        file_ext = filename.lower().split('.')[-1]
        
        if file_ext == 'pdf':
            return self._extract_pdf_text(file_path)
        elif file_ext in ['docx', 'doc']:
            return self._extract_word_text(file_path)
        elif file_ext in ['xlsx', 'xls']:
            return self._extract_excel_text(file_path)
        elif file_ext == 'csv':
            return self._extract_csv_text(file_path)
        elif file_ext == 'txt':
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        elif file_ext in ['eml', 'msg']:
            return self._extract_email_text(file_path)
        else:
            raise ValueError(f\"Unsupported file type: {file_ext}\")
    
    def _extract_pdf_text(self, file_path: str) -> str:
        \"\"\"Extract text from PDF\"\"\"
        text_content = \"\"
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text_content += page.extract_text() + \"\\n\"
        return text_content
    
    def _extract_excel_text(self, file_path: str) -> str:
        \"\"\"Extract text from Excel file\"\"\"
        df = pd.read_excel(file_path, sheet_name=None)  # Read all sheets
        text_content = \"\"
        for sheet_name, sheet_df in df.items():
            text_content += f\"Sheet: {sheet_name}\\n\"
            text_content += sheet_df.to_string() + \"\\n\\n\"
        return text_content
```

### 3. Agent Registry & Orchestration

```python
# src/hub/services/agent_orchestrator.py
from typing import Dict, List, Optional
import asyncio
import aiohttp

class AgentOrchestrator:
    \"\"\"Manage spoke agent registry and route collaboration requests\"\"\"
    
    def __init__(self, hub_llm: UnifiedHubLLM):
        self.hub_llm = hub_llm
        self.agent_registry = {}
        self.collaboration_history = []
        
    async def register_agent(self, registration_data: Dict) -> Dict:
        \"\"\"Register new spoke agent with attestation verification\"\"\"
        agent_id = registration_data[\"agent_id\"]
        
        # Verify attestation
        verification_result = await self._verify_agent_attestation(registration_data)
        
        if verification_result[\"verified\"]:
            self.agent_registry[agent_id] = {
                \"agent_id\": agent_id,
                \"agent_type\": registration_data[\"agent_type\"],
                \"capabilities\": registration_data[\"capabilities\"],
                \"endpoint\": registration_data[\"endpoint\"],
                \"attestation_endpoint\": registration_data[\"attestation_endpoint\"],
                \"public_key\": registration_data[\"attestation_data\"][\"public_key\"],
                \"attestation_quote\": registration_data[\"attestation_data\"][\"quote\"],
                \"status\": \"verified\",
                \"registered_at\": datetime.utcnow().isoformat(),
                \"last_seen\": datetime.utcnow().isoformat()
            }
            
            return {
                \"status\": \"registered\",
                \"verification_status\": \"verified\",
                \"agent_id\": agent_id
            }
        else:
            return {
                \"status\": \"rejected\",
                \"verification_status\": \"failed\",
                \"error\": verification_result[\"error\"]
            }
    
    async def route_collaboration_request(self, request_data: Dict) -> Dict:
        \"\"\"Route collaboration request to best available agent\"\"\"
        query = request_data[\"query\"]
        requesting_agent = request_data[\"requesting_agent\"]
        
        # Get available agents
        available_agents = [
            agent for agent in self.agent_registry.values()
            if agent[\"status\"] == \"verified\" and agent[\"agent_id\"] != requesting_agent
        ]
        
        if not available_agents:
            return {\"error\": \"No verified agents available for collaboration\"}
        
        # Use LLM to route request
        routing_decision = self.hub_llm.route_agent_request(query, available_agents)
        
        target_agent = None
        for agent in available_agents:
            if agent[\"agent_type\"] == routing_decision[\"best_agent\"]:
                target_agent = agent
                break
        
        if not target_agent:
            return {\"error\": f\"Target agent {routing_decision['best_agent']} not found\"}
        
        # Prepare data package for target agent
        data_package = await self._prepare_data_package(request_data, target_agent)
        
        return {
            \"routing_id\": f\"route_{uuid.uuid4().hex[:8]}\",
            \"target_agent\": target_agent[\"agent_id\"],
            \"reasoning\": routing_decision[\"reasoning\"],
            \"estimated_time_minutes\": routing_decision[\"estimated_time\"],
            \"data_package\": data_package,
            \"routed_at\": datetime.utcnow().isoformat()
        }
    
    async def _prepare_data_package(self, request_data: Dict, target_agent: Dict) -> Dict:
        \"\"\"Prepare encrypted data package for target agent\"\"\"
        # Get relevant data based on request
        relevant_data = await self._fetch_relevant_data(request_data)
        
        # Encrypt data using target agent's public key
        encrypted_data = self._encrypt_for_agent(relevant_data, target_agent[\"public_key\"])
        
        return {
            \"encrypted_data\": encrypted_data,
            \"encryption_method\": \"agent_public_key\",
            \"data_types\": request_data.get(\"data_requirements\", []),
            \"context\": request_data.get(\"context\", {})
        }
```

### 4. Attestation Discovery Service

```python
# src/hub/services/attestation_discovery.py
import base64
import json
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ed25519

class AttestationDiscoveryService:
    \"\"\"Manage attestation discovery and verification for agents\"\"\"
    
    def __init__(self):
        self.verified_agents = {}
        self.attestation_log = []
        
    async def verify_agent_attestation(self, attestation_data: Dict) -> Dict:
        \"\"\"Verify agent's attestation quote and public key\"\"\"
        try:
            # Decode attestation quote
            quote = base64.b64decode(attestation_data[\"quote\"])
            public_key_pem = attestation_data[\"public_key\"]
            
            # Verify quote signature and extract measurements
            verification_result = self._verify_tdx_quote(quote)
            
            if verification_result[\"valid\"]:
                # Store verified agent info
                agent_id = attestation_data.get(\"agent_id\")
                self.verified_agents[agent_id] = {
                    \"agent_id\": agent_id,
                    \"public_key\": public_key_pem,
                    \"measurements\": verification_result[\"measurements\"],
                    \"verified_at\": datetime.utcnow().isoformat(),
                    \"expires_at\": (datetime.utcnow() + timedelta(hours=4)).isoformat()
                }
                
                return {\"verified\": True, \"measurements\": verification_result[\"measurements\"]}
            else:
                return {\"verified\": False, \"error\": verification_result[\"error\"]}
                
        except Exception as e:
            return {\"verified\": False, \"error\": f\"Attestation verification failed: {str(e)}\"}
    
    def get_verified_agents(self) -> List[Dict]:
        \"\"\"Get list of all currently verified agents\"\"\"
        current_time = datetime.utcnow()
        verified_agents = []
        
        for agent_id, agent_info in self.verified_agents.items():
            expires_at = datetime.fromisoformat(agent_info[\"expires_at\"])
            if current_time < expires_at:
                verified_agents.append(agent_info)
            else:
                # Remove expired attestation
                del self.verified_agents[agent_id]
        
        return verified_agents
    
    async def log_attestation_event(self, event_data: Dict):
        \"\"\"Log attestation-related events for audit\"\"\"
        log_entry = {
            \"timestamp\": datetime.utcnow().isoformat(),
            \"event_type\": event_data[\"event_type\"],
            \"requesting_agent\": event_data.get(\"requesting_agent\"),
            \"target_agent\": event_data.get(\"target_agent\"),
            \"verification_result\": event_data.get(\"verification_result\"),
            \"details\": event_data.get(\"details\", {})
        }
        
        self.attestation_log.append(log_entry)
        
        # Keep only last 1000 log entries
        if len(self.attestation_log) > 1000:
            self.attestation_log = self.attestation_log[-1000:]
```

---

## Docker Implementation

### Hub Dockerfile
```dockerfile
# hub/Dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    curl wget git build-essential \\
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download and cache Llama-3.2-1B-Instruct
RUN python -c \"
import os
os.environ['HF_HOME'] = '/app/models'
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

print('Downloading Llama-3.2-1B-Instruct...')
tokenizer = AutoTokenizer.from_pretrained('meta-llama/Llama-3.2-1B-Instruct')
model = AutoModelForCausalLM.from_pretrained(
    'meta-llama/Llama-3.2-1B-Instruct',
    torch_dtype=torch.float16,
    device_map='cpu',
    low_cpu_mem_usage=True
)
print('Hub model cached successfully')
\"

# Copy hub application code
COPY src/ /app/src/
COPY config/ /app/config/

# Create necessary directories
RUN mkdir -p /app/data /app/logs /app/crypto /app/models

# Set environment variables
ENV PYTHONPATH=/app/src
ENV TRANSFORMERS_CACHE=/app/models
ENV HF_HOME=/app/models

# Create non-root user
RUN useradd -m -u 1000 hubuser && chown -R hubuser:hubuser /app
USER hubuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \\
  CMD curl -f http://localhost:8080/health || exit 1

# Start hub service
CMD [\"python\", \"/app/src/hub/main.py\"]
```

### Hub Docker Compose
```yaml
# hub/docker-compose.yaml
version: '3.8'

services:
  boardroom-hub:
    build:
      context: .
      dockerfile: Dockerfile
    image: hub-boardroom-tee:latest
    container_name: boardroom-hub-${CLIENT_ID}
    
    environment:
      - HUB_MODEL_NAME=meta-llama/Llama-3.2-1B-Instruct
      - HUB_MAX_MEMORY_MB=3000
      - HUB_API_PORT=8080
      - HUB_ATTESTATION_PORT=29343
      - CLIENT_ID=${CLIENT_ID}
      - LOG_LEVEL=INFO
    
    ports:
      - \"8080:8080\"
      - \"29343:29343\"
    
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
      - ./config:/app/config
      - ./crypto:/app/crypto  # TEE-generated keys
    
    networks:
      - boardroom-network
    
    restart: unless-stopped
    
    deploy:
      resources:
        limits:
          memory: 4G
          cpus: '2'
        reservations:
          memory: 2G
          cpus: '1'

networks:
  boardroom-network:
    external: true
```

---

## Configuration Files

### Hub Configuration
```yaml
# config/hub_config.yaml
hub:
  model_name: \"meta-llama/Llama-3.2-1B-Instruct\"
  max_memory_mb: 3000
  api_port: 8080
  attestation_port: 29343
  
  # Data processing settings
  processing:
    batch_size: 10
    max_file_size_mb: 100
    supported_formats: [\"pdf\", \"docx\", \"xlsx\", \"csv\", \"txt\", \"eml\"]
    processing_timeout_hours: 24
  
  # Agent management
  agents:
    max_registered_agents: 50
    attestation_validity_hours: 4
    collaboration_timeout_seconds: 30
  
  # Storage settings
  storage:
    data_retention_days: 365
    max_storage_gb: 1000
    backup_enabled: true

# Security settings
security:
  tee_platform: \"secretvm\"
  attestation_required: true
  encryption_algorithm: \"AES-256-GCM\"
  key_rotation_hours: 24

# Logging configuration
logging:
  level: \"INFO\"
  format: \"json\"
  audit_enabled: true
  retention_days: 90
```

### Environment Variables
```bash
# hub/.env
HUB_MODEL_NAME=meta-llama/Llama-3.2-1B-Instruct
HUB_MAX_MEMORY_MB=3000
HUB_API_PORT=8080
HUB_ATTESTATION_PORT=29343
CLIENT_ID=client-unique-identifier
LOG_LEVEL=INFO

# Database settings
DATABASE_URL=sqlite:///app/data/hub.db

# Storage settings
STORAGE_PATH=/app/data
MAX_STORAGE_GB=1000

# Security settings
TEE_PLATFORM=secretvm
ATTESTATION_REQUIRED=true
```

---

## API Endpoints Implementation

### FastAPI Application
```python
# src/hub/main.py
import asyncio
import logging
from fastapi import FastAPI, HTTPException, UploadFile, File, Depends
from contextlib import asynccontextmanager

from src.hub.services.unified_hub_llm import UnifiedHubLLM
from src.hub.services.document_processor import DocumentProcessor
from src.hub.services.agent_orchestrator import AgentOrchestrator
from src.hub.services.attestation_discovery import AttestationDiscoveryService
from src.hub.api.routes import hub_router

# Global services
hub_llm = None
document_processor = None
agent_orchestrator = None
attestation_service = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global hub_llm, document_processor, agent_orchestrator, attestation_service
    
    logging.info(\"Starting Boardroom TEE Hub...\")
    
    # Initialize unified LLM
    hub_llm = UnifiedHubLLM()
    await hub_llm.load_model()
    
    # Initialize services
    document_processor = DocumentProcessor(hub_llm)
    agent_orchestrator = AgentOrchestrator(hub_llm)
    attestation_service = AttestationDiscoveryService()
    
    logging.info(\"Hub services initialized successfully\")
    
    yield
    
    # Shutdown
    logging.info(\"Shutting down hub services...\")
    if hub_llm:
        hub_llm.cleanup_memory()

# Create FastAPI app
app = FastAPI(
    title=\"Boardroom TEE Hub\",
    description=\"Central hub for document processing and agent orchestration\",
    version=\"1.0.0\",
    lifespan=lifespan
)

# Include API routes
app.include_router(hub_router, prefix=\"/api/v1\")

@app.get(\"/health\")
async def health_check():
    return {
        \"status\": \"healthy\",
        \"model_loaded\": hub_llm.is_loaded if hub_llm else False,
        \"memory_usage\": hub_llm.get_memory_usage() if hub_llm else None,
        \"registered_agents\": len(agent_orchestrator.agent_registry) if agent_orchestrator else 0
    }

if __name__ == \"__main__\":
    import uvicorn
    uvicorn.run(
        \"main:app\",
        host=\"0.0.0.0\",
        port=8080,
        log_level=\"info\"
    )
```

---

*Last Updated: December 2024*  
*Related: [`04-apis/api-specifications.md`](../04-apis/api-specifications.md) for complete API documentation*  
*Purpose: Complete hub implementation for Claude code generation*