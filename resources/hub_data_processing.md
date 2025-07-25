# Hub Data Processing Pipeline - Llama-3.2-1B-Instruct Unified Architecture

## Overview
The hub uses **Llama-3.2-1B-Instruct** as a unified model for both document processing and agent orchestration. This single-model approach optimizes resource usage within the medium instance (2 vCPU, 4GB RAM) constraint while providing excellent instruction-following capabilities for all hub operations.

---

## Unified LLM Architecture

### Single Model for All Operations
**Model**: Llama-3.2-1B-Instruct
**Instance**: Medium (2 vCPU, 4GB RAM, 40GB Storage)
**Memory Usage**: ~2GB model + 1GB overhead = 3GB total
**Available RAM**: 1GB remaining for processing

**Unified Capabilities**:
- **Document Processing**: Categorization and indexing of uploaded files
- **Agent Orchestration**: Intelligent routing and coordination of agent requests
- **Context Management**: Maintains state across multi-agent workflows
- **Always Available**: Single model stays loaded for all operations

### Model Configuration
```python
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from typing import Dict, Optional
import gc

class UnifiedHubLLM:
    """Single Llama-3.2-1B-Instruct model for all hub operations"""
    
    def __init__(self):
        self.model_name = "meta-llama/Llama-3.2-1B-Instruct"
        self.model = None
        self.tokenizer = None
        self.is_loaded = False
    
    def load_model(self):
        """Load single 1B model for all hub operations"""
        if self.is_loaded:
            return
            
        try:
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            
            # Load model with memory optimization for 4GB RAM
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                torch_dtype=torch.float16,  # Reduce memory usage
                device_map="cpu",           # CPU inference for TEE compatibility
                low_cpu_mem_usage=True,     # Optimize for limited RAM
                use_cache=False             # Disable KV cache to save memory
            )
            
            # Set padding token if not present
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            self.is_loaded = True
            
        except Exception as e:
            raise Exception(f"Failed to load model: {str(e)}")
    
    def get_model(self):
        """Get loaded model and tokenizer"""
        if not self.is_loaded:
            self.load_model()
        return self.model, self.tokenizer
    
    def get_memory_usage(self) -> dict:
        """Get current memory usage information"""
        import psutil
        process = psutil.Process()
        memory_mb = process.memory_info().rss / 1024 / 1024
        
        return {
            "model_loaded": self.is_loaded,
            "memory_usage_mb": memory_mb,
            "model_name": self.model_name,
            "available_memory_mb": 4096 - memory_mb  # Assuming 4GB total
        }
    
    def cleanup_memory(self):
        """Force garbage collection to free memory"""
        gc.collect()
        torch.cuda.empty_cache() if torch.cuda.is_available() else None

# Global hub LLM instance
hub_llm = UnifiedHubLLM()
```

### Docker Configuration
```dockerfile
# Updated Dockerfile for single model
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download model during build (offline capability)
RUN python -c "
from transformers import AutoTokenizer, AutoModelForCausalLM
model_name = 'meta-llama/Llama-3.2-1B-Instruct'
AutoTokenizer.from_pretrained(model_name)
AutoModelForCausalLM.from_pretrained(model_name)
print('Model downloaded successfully')
"

WORKDIR /app
COPY . .

# Set environment variables
ENV HUB_MODEL_NAME=meta-llama/Llama-3.2-1B-Instruct
ENV HUB_MAX_MEMORY_MB=3000
ENV TRANSFORMERS_CACHE=/app/models

CMD ["python", "main.py"]
```

---

## Document Processing Pipeline

### 1. File Upload and Validation
```python
import mimetypes
import hashlib
from typing import Dict, List, Optional

SUPPORTED_TYPES = {
    'application/pdf': '.pdf',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': '.docx',
    'application/vnd.ms-excel': '.xls',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': '.xlsx',
    'text/csv': '.csv',
    'text/plain': '.txt',
    'message/rfc822': '.eml'
}

MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB limit

async def validate_upload(file_data: bytes, filename: str) -> Dict:
    """Validate uploaded file before processing"""
    
    # Size check
    if len(file_data) > MAX_FILE_SIZE:
        raise ValueError(f"File too large: {len(file_data)} bytes")
    
    # Type validation
    mime_type, _ = mimetypes.guess_type(filename)
    if mime_type not in SUPPORTED_TYPES:
        raise ValueError(f"Unsupported file type: {mime_type}")
    
    # Generate file hash for deduplication
    file_hash = hashlib.sha256(file_data).hexdigest()
    
    return {
        "filename": filename,
        "size": len(file_data),
        "mime_type": mime_type,
        "hash": file_hash,
        "status": "validated"
    }
```

### 2. Content Extraction by File Type
```python
import PyPDF2
import pandas as pd
import docx
import email
from io import BytesIO

class ContentExtractor:
    """Extract text content from various file types"""
    
    @staticmethod
    def extract_pdf(file_data: bytes) -> str:
        """Extract text from PDF files"""
        try:
            pdf_file = BytesIO(file_data)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\\n"
            return text.strip()
        except Exception as e:
            raise ValueError(f"PDF extraction failed: {str(e)}")
    
    @staticmethod
    def extract_docx(file_data: bytes) -> str:
        """Extract text from Word documents"""
        try:
            doc_file = BytesIO(file_data)
            doc = docx.Document(doc_file)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\\n"
            return text.strip()
        except Exception as e:
            raise ValueError(f"DOCX extraction failed: {str(e)}")
    
    @staticmethod
    def extract_excel(file_data: bytes) -> str:
        """Extract text from Excel files"""
        try:
            excel_file = BytesIO(file_data)
            # Read all sheets and combine
            xlsx = pd.ExcelFile(excel_file)
            all_text = []
            
            for sheet_name in xlsx.sheet_names:
                df = pd.read_excel(xlsx, sheet_name=sheet_name)
                # Convert to string and combine
                sheet_text = df.to_string(index=False, na_rep='')
                all_text.append(f"Sheet: {sheet_name}\\n{sheet_text}")
            
            return "\\n\\n".join(all_text)
        except Exception as e:
            raise ValueError(f"Excel extraction failed: {str(e)}")
    
    @staticmethod
    def extract_csv(file_data: bytes) -> str:
        """Extract text from CSV files"""
        try:
            csv_file = BytesIO(file_data)
            df = pd.read_csv(csv_file)
            return df.to_string(index=False, na_rep='')
        except Exception as e:
            raise ValueError(f"CSV extraction failed: {str(e)}")
    
    @staticmethod
    def extract_email(file_data: bytes) -> str:
        """Extract text from email files"""
        try:
            email_content = email.message_from_bytes(file_data)
            
            # Extract headers
            subject = email_content.get('Subject', '')
            from_addr = email_content.get('From', '')
            to_addr = email_content.get('To', '')
            date = email_content.get('Date', '')
            
            # Extract body
            body = ""
            if email_content.is_multipart():
                for part in email_content.walk():
                    if part.get_content_type() == "text/plain":
                        body += part.get_payload(decode=True).decode('utf-8', errors='ignore')
            else:
                body = email_content.get_payload(decode=True).decode('utf-8', errors='ignore')
            
            return f"Subject: {subject}\\nFrom: {from_addr}\\nTo: {to_addr}\\nDate: {date}\\n\\nBody:\\n{body}"
        except Exception as e:
            raise ValueError(f"Email extraction failed: {str(e)}")
    
    def extract_content(self, file_data: bytes, mime_type: str) -> str:
        """Route to appropriate extraction method"""
        extractors = {
            'application/pdf': self.extract_pdf,
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document': self.extract_docx,
            'application/vnd.ms-excel': self.extract_excel,
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': self.extract_excel,
            'text/csv': self.extract_csv,
            'text/plain': lambda data: data.decode('utf-8', errors='ignore'),
            'message/rfc822': self.extract_email
        }
        
        extractor = extractors.get(mime_type)
        if not extractor:
            raise ValueError(f"No extractor for mime type: {mime_type}")
        
        return extractor(file_data)
```

### 3. Llama-3.2-1B-Instruct Categorization
```python
import re
import json
from datetime import datetime
from typing import Dict, List

class DocumentCategorizer:
    """Use unified Llama-3.2-1B-Instruct for document analysis and categorization"""
    
    def __init__(self, hub_llm: UnifiedHubLLM):
        self.hub_llm = hub_llm
    
    def create_categorization_prompt(self, content: str, filename: str) -> str:
        """Create instruction prompt for document categorization"""
        
        # Truncate content if too long (keep first 2000 chars for context)
        truncated_content = content[:2000] + "..." if len(content) > 2000 else content
        
        prompt = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>

You are a document analysis expert. Analyze documents and provide structured categorization metadata.

<|eot_id|><|start_header_id|>user<|end_header_id|>

Analyze this document and provide categorization metadata in valid JSON format.

Filename: {filename}
Content: {truncated_content}

Categorize based on this criteria:
- Department: Finance, Marketing, Sales, Operations, Other
- Document Type: Report, Data/Spreadsheet, Email, Planning, Contract
- Extract 5-10 key terms that represent the main topics
- Find any dates mentioned in the content
- Provide a brief 1-sentence summary

Respond with ONLY valid JSON in this exact format:
{{
  "department": "Finance",
  "document_type": "Report", 
  "key_terms": ["budget", "revenue", "quarterly"],
  "dates_mentioned": ["2024-Q3", "January 2024"],
  "summary": "Brief description of document content and purpose.",
  "confidence_score": 0.85
}}

<|eot_id|><|start_header_id|>assistant<|end_header_id|>

"""
        return prompt
    
    def generate_categorization(self, prompt: str) -> Dict:
        """Generate categorization using unified hub model"""
        model, tokenizer = self.hub_llm.get_model()
        try:
            # Tokenize input
            inputs = tokenizer(
                prompt, 
                return_tensors="pt", 
                truncation=True, 
                max_length=4096,
                padding=True
            )
            
            # Generate response
            with torch.no_grad():
                outputs = model.generate(
                    **inputs,
                    max_new_tokens=300,
                    temperature=0.1,  # Low temperature for consistent output
                    do_sample=True,
                    pad_token_id=tokenizer.eos_token_id,
                    eos_token_id=tokenizer.eos_token_id
                )
            
            # Decode response
            response = tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Extract JSON from response (after the assistant header)
            json_start = response.find('{"')
            if json_start == -1:
                json_start = response.find('{\\n')
            
            if json_start != -1:
                json_text = response[json_start:]
                # Clean up any trailing text after JSON
                json_end = json_text.rfind('}') + 1
                json_text = json_text[:json_end]
                
                return json.loads(json_text)
            else:
                raise ValueError("No valid JSON found in response")
                
        except Exception as e:
            # Fallback categorization if model fails
            return self.create_fallback_categorization(prompt, str(e))
    
    def create_fallback_categorization(self, prompt: str, error: str) -> Dict:
        """Create basic categorization if model fails"""
        # Simple keyword-based fallback
        content_lower = prompt.lower()
        
        # Department detection
        if any(term in content_lower for term in ['budget', 'revenue', 'financial', 'cost', 'profit']):
            department = "Finance"
        elif any(term in content_lower for term in ['marketing', 'campaign', 'customer', 'brand']):
            department = "Marketing"  
        elif any(term in content_lower for term in ['sales', 'deal', 'pipeline', 'commission']):
            department = "Sales"
        elif any(term in content_lower for term in ['operations', 'process', 'workflow', 'production']):
            department = "Operations"
        else:
            department = "Other"
        
        # Document type detection
        if any(term in content_lower for term in ['report', 'analysis', 'summary']):
            doc_type = "Report"
        elif any(term in content_lower for term in ['spreadsheet', 'data', 'table', 'csv']):
            doc_type = "Data/Spreadsheet"
        elif any(term in content_lower for term in ['email', 'subject:', 'from:']):
            doc_type = "Email"
        elif any(term in content_lower for term in ['plan', 'strategy', 'roadmap']):
            doc_type = "Planning"
        else:
            doc_type = "Report"
        
        # Extract basic dates
        date_pattern = r'\\b\\d{4}[-/]\\d{1,2}[-/]\\d{1,2}\\b|\\b\\d{1,2}[-/]\\d{1,2}[-/]\\d{4}\\b'
        dates = re.findall(date_pattern, content_lower)
        
        return {
            "department": department,
            "document_type": doc_type,
            "key_terms": ["document", "content", "analysis"],
            "dates_mentioned": dates[:3],  # Limit to first 3 dates
            "summary": f"Document categorized using fallback method due to processing error: {error}",
            "confidence_score": 0.3,
            "fallback_used": True
        }
    
    def process_document(self, content: str, filename: str) -> Dict:
        """Complete document processing pipeline"""
        try:
            # Create categorization prompt
            prompt = self.create_categorization_prompt(content, filename)
            
            # Generate categorization
            categorization = self.generate_categorization(prompt)
            
            # Add processing metadata
            categorization.update({
                "processed_at": datetime.utcnow().isoformat(),
                "content_length": len(content),
                "model_used": "Llama-3.2-1B-Instruct",
                "processing_status": "success"
            })
            
            return categorization
            
        except Exception as e:
            # Return error categorization
            return {
                "department": "Other",
                "document_type": "Report", 
                "key_terms": ["error", "processing", "failed"],
                "dates_mentioned": [],
                "summary": f"Document processing failed: {str(e)}",
                "confidence_score": 0.0,
                "processed_at": datetime.utcnow().isoformat(),
                "content_length": len(content),
                "model_used": "Llama-3.2-1B-Instruct",
                "processing_status": "error",
                "error_details": str(e)
            }
```

---

## Data Storage and Indexing

### Storage Structure
```python
import sqlite3
import json
from pathlib import Path

class HubDataStorage:
    """Handle data storage and indexing for processed documents"""
    
    def __init__(self, client_id: str, storage_path: Path):
        self.client_id = client_id
        self.storage_path = storage_path / client_id
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize database
        self.db_path = self.storage_path / "metadata.db"
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database for metadata storage"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS documents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filename TEXT NOT NULL,
                    file_hash TEXT UNIQUE NOT NULL,
                    mime_type TEXT NOT NULL,
                    file_size INTEGER NOT NULL,
                    department TEXT NOT NULL,
                    document_type TEXT NOT NULL,
                    key_terms TEXT NOT NULL,  -- JSON array
                    dates_mentioned TEXT,     -- JSON array  
                    summary TEXT NOT NULL,
                    confidence_score REAL NOT NULL,
                    content_length INTEGER NOT NULL,
                    processed_at TEXT NOT NULL,
                    processing_status TEXT NOT NULL,
                    error_details TEXT,
                    file_path TEXT NOT NULL,
                    content_path TEXT NOT NULL
                )
            """)
            
            # Create indexes for fast querying
            conn.execute("CREATE INDEX IF NOT EXISTS idx_department ON documents(department)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_document_type ON documents(document_type)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_file_hash ON documents(file_hash)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_processed_at ON documents(processed_at)")
    
    def store_document(self, file_data: bytes, content: str, 
                      metadata: Dict, categorization: Dict) -> str:
        """Store document and return document ID"""
        
        # Create file paths
        file_path = self.storage_path / "files" / f"{metadata['hash']}{SUPPORTED_TYPES.get(metadata['mime_type'], '.bin')}"
        content_path = self.storage_path / "content" / f"{metadata['hash']}.txt"
        
        # Create directories
        file_path.parent.mkdir(exist_ok=True)
        content_path.parent.mkdir(exist_ok=True)
        
        # Store original file (encrypted in TEE)
        with open(file_path, 'wb') as f:
            f.write(file_data)
        
        # Store extracted content
        with open(content_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Store metadata in database
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                INSERT INTO documents (
                    filename, file_hash, mime_type, file_size,
                    department, document_type, key_terms, dates_mentioned,
                    summary, confidence_score, content_length, processed_at,
                    processing_status, error_details, file_path, content_path
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                metadata['filename'], metadata['hash'], metadata['mime_type'], metadata['size'],
                categorization['department'], categorization['document_type'], 
                json.dumps(categorization['key_terms']), json.dumps(categorization['dates_mentioned']),
                categorization['summary'], categorization['confidence_score'], 
                categorization['content_length'], categorization['processed_at'],
                categorization['processing_status'], categorization.get('error_details'),
                str(file_path), str(content_path)
            ))
            
            return str(cursor.lastrowid)
    
    def search_documents(self, query_params: Dict) -> List[Dict]:
        """Search documents based on various criteria"""
        
        conditions = []
        params = []
        
        # Build dynamic query
        if 'department' in query_params:
            conditions.append("department = ?")
            params.append(query_params['department'])
        
        if 'document_type' in query_params:
            conditions.append("document_type = ?")
            params.append(query_params['document_type'])
        
        if 'keywords' in query_params:
            # Search in key_terms and summary
            conditions.append("(key_terms LIKE ? OR summary LIKE ?)")
            keyword_pattern = f"%{query_params['keywords']}%"
            params.extend([keyword_pattern, keyword_pattern])
        
        if 'date_from' in query_params:
            conditions.append("processed_at >= ?")
            params.append(query_params['date_from'])
        
        if 'date_to' in query_params:
            conditions.append("processed_at <= ?")
            params.append(query_params['date_to'])
        
        # Build final query
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        query = f"""
            SELECT * FROM documents 
            WHERE {where_clause}
            ORDER BY processed_at DESC
            LIMIT ?
        """
        params.append(query_params.get('limit', 100))
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(query, params)
            
            results = []
            for row in cursor.fetchall():
                doc = dict(row)
                # Parse JSON fields
                doc['key_terms'] = json.loads(doc['key_terms'])
                doc['dates_mentioned'] = json.loads(doc['dates_mentioned']) if doc['dates_mentioned'] else []
                results.append(doc)
            
            return results
```

---

## Integration with Attestation System

### Spoke Agent Data Requests
```python
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
import base64

class SecureDataDistribution:
    """Handle secure data distribution to spoke agents using attestation"""
    
    def __init__(self, hub_private_key_path: str, storage: HubDataStorage):
        self.storage = storage
        
        # Load hub private key
        with open(hub_private_key_path, 'rb') as f:
            self.hub_private_key = serialization.load_pem_private_key(
                f.read(), password=None
            )
    
    def verify_spoke_attestation(self, attestation_quote: str, 
                               spoke_public_key: str) -> bool:
        """Verify spoke agent attestation before data sharing"""
        # This would integrate with your existing attestation service
        # For now, placeholder logic
        try:
            # In production, validate against known measurements
            # and verify attestation quote signatures
            return True  # Placeholder
        except Exception:
            return False
    
    def encrypt_data_for_spoke(self, data: Dict, spoke_public_key_pem: str) -> str:
        """Encrypt data using spoke agent's public key"""
        try:
            # Load spoke public key
            spoke_public_key = serialization.load_pem_public_key(
                spoke_public_key_pem.encode()
            )
            
            # Serialize data
            data_bytes = json.dumps(data).encode()
            
            # Encrypt with spoke's public key
            encrypted_data = spoke_public_key.encrypt(
                data_bytes,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            
            # Return base64 encoded
            return base64.b64encode(encrypted_data).decode()
            
        except Exception as e:
            raise ValueError(f"Encryption failed: {str(e)}")
    
    def handle_spoke_data_request(self, request: Dict) -> Dict:
        """Handle data request from spoke agent with attestation verification"""
        
        # Verify attestation
        if not self.verify_spoke_attestation(
            request['attestation_quote'], 
            request['spoke_public_key']
        ):
            return {
                "status": "error",
                "error": "Attestation verification failed",
                "data": None
            }
        
        try:
            # Search for requested documents
            search_results = self.storage.search_documents(request['query_params'])
            
            # Load content for matching documents
            response_data = []
            for doc in search_results:
                # Read content file
                with open(doc['content_path'], 'r', encoding='utf-8') as f:
                    content = f.read()
                
                response_data.append({
                    "document_id": doc['id'],
                    "filename": doc['filename'],
                    "department": doc['department'],
                    "document_type": doc['document_type'],
                    "key_terms": doc['key_terms'],
                    "summary": doc['summary'],
                    "content": content,
                    "confidence_score": doc['confidence_score'],
                    "processed_at": doc['processed_at']
                })
            
            # Encrypt response for spoke agent
            encrypted_data = self.encrypt_data_for_spoke(
                response_data, 
                request['spoke_public_key']
            )
            
            return {
                "status": "success",
                "encrypted_data": encrypted_data,
                "document_count": len(response_data),
                "query_processed_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "error", 
                "error": f"Data request failed: {str(e)}",
                "data": None
            }
```

---

## Performance Optimization

### Memory Management
```python
import gc
import psutil
from typing import Generator

class OptimizedProcessor:
    """Optimized document processor for resource-constrained environment"""
    
    def __init__(self, model, tokenizer, max_memory_mb: int = 3000):
        self.model = model
        self.tokenizer = tokenizer
        self.max_memory_mb = max_memory_mb
        
    def check_memory_usage(self) -> float:
        """Check current memory usage percentage"""
        process = psutil.Process()
        memory_mb = process.memory_info().rss / 1024 / 1024
        return memory_mb
    
    def process_documents_batch(self, documents: List[Dict]) -> Generator[Dict, None, None]:
        """Process documents in memory-safe batches"""
        
        for doc in documents:
            # Check memory before processing
            current_memory = self.check_memory_usage()
            
            if current_memory > self.max_memory_mb:
                # Force garbage collection
                gc.collect()
                torch.cuda.empty_cache() if torch.cuda.is_available() else None
                
                # Check again
                current_memory = self.check_memory_usage()
                if current_memory > self.max_memory_mb:
                    yield {
                        "error": "Memory limit exceeded",
                        "document": doc,
                        "memory_usage_mb": current_memory
                    }
                    continue
            
            try:
                # Process single document
                result = self.process_single_document(doc)
                yield result
                
                # Clean up after each document
                gc.collect()
                
            except Exception as e:
                yield {
                    "error": str(e),
                    "document": doc,
                    "memory_usage_mb": current_memory
                }
    
    def process_single_document(self, doc: Dict) -> Dict:
        """Process single document with memory cleanup"""
        try:
            # Extract content
            extractor = ContentExtractor()
            content = extractor.extract_content(doc['file_data'], doc['mime_type'])
            
            # Categorize with model
            categorizer = DocumentCategorizer(self.model, self.tokenizer)
            categorization = categorizer.process_document(content, doc['filename'])
            
            return {
                "status": "success",
                "document": doc,
                "content": content,
                "categorization": categorization
            }
            
        finally:
            # Always clean up
            gc.collect()
```

### Processing Queue Management
```python
import asyncio
from enum import Enum
from dataclasses import dataclass
from typing import Optional

class ProcessingStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing" 
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class ProcessingJob:
    job_id: str
    client_id: str
    filename: str
    file_data: bytes
    mime_type: str
    status: ProcessingStatus
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    result: Optional[Dict] = None

class ProcessingQueue:
    """Manage document processing queue with 2-24 hour batch processing"""
    
    def __init__(self):
        self.queue: List[ProcessingJob] = []
        self.processing = False
        
    async def add_job(self, job: ProcessingJob):
        """Add job to processing queue"""
        self.queue.append(job)
        
        # Start processing if not already running
        if not self.processing:
            asyncio.create_task(self.process_queue())
    
    async def process_queue(self):
        """Process all queued jobs in batch"""
        if self.processing:
            return
            
        self.processing = True
        
        try:
            # Initialize model and processors
            model, tokenizer = self.load_model()
            processor = OptimizedProcessor(model, tokenizer)
            
            # Process jobs in batches by client
            client_jobs = {}
            for job in self.queue:
                if job.status == ProcessingStatus.PENDING:
                    if job.client_id not in client_jobs:
                        client_jobs[job.client_id] = []
                    client_jobs[job.client_id].append(job)
            
            # Process each client's documents
            for client_id, jobs in client_jobs.items():
                storage = HubDataStorage(client_id, Path("/app/data/storage"))
                
                for job in jobs:
                    job.status = ProcessingStatus.PROCESSING
                    job.started_at = datetime.utcnow()
                    
                    try:
                        # Process document
                        result = processor.process_single_document({
                            'file_data': job.file_data,
                            'filename': job.filename,
                            'mime_type': job.mime_type
                        })
                        
                        if result['status'] == 'success':
                            # Store in database
                            doc_id = storage.store_document(
                                job.file_data,
                                result['content'], 
                                {
                                    'filename': job.filename,
                                    'mime_type': job.mime_type,
                                    'size': len(job.file_data),
                                    'hash': hashlib.sha256(job.file_data).hexdigest()
                                },
                                result['categorization']
                            )
                            
                            job.result = {"document_id": doc_id, **result['categorization']}
                            job.status = ProcessingStatus.COMPLETED
                        else:
                            job.status = ProcessingStatus.FAILED
                            job.error_message = result.get('error', 'Unknown error')
                        
                    except Exception as e:
                        job.status = ProcessingStatus.FAILED
                        job.error_message = str(e)
                    
                    finally:
                        job.completed_at = datetime.utcnow()
                        
                        # Small delay between documents
                        await asyncio.sleep(0.1)
        
        finally:
            self.processing = False
    
    def get_job_status(self, job_id: str) -> Optional[ProcessingJob]:
        """Get status of specific job"""
        for job in self.queue:
            if job.job_id == job_id:
                return job
        return None
    
    def load_model(self):
        """Load Llama model for processing"""
        # This would be cached/singleton in production
        tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-3.2-1B-Instruct")
        model = AutoModelForCausalLM.from_pretrained(
            "meta-llama/Llama-3.2-1B-Instruct",
            torch_dtype=torch.float16,
            device_map="cpu",
            low_cpu_mem_usage=True
        )
        return model, tokenizer
```

---

This comprehensive document covers the complete Llama-3.2-1B-Instruct implementation for the hub's data processing pipeline, including file handling, content extraction, AI categorization, secure storage, and attestation-based data distribution to spoke agents.

*Last Updated: [Current Date]*  
*Related: hub_architecture.md, security_model.md, api_specifications.md*
