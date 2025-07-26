"""Document processing service for Hub."""

import os
import logging
import hashlib
import json
from typing import Dict, Optional
from datetime import datetime
import uuid
import PyPDF2
import pandas as pd
from docx import Document as DocxDocument
import email
from email import policy
from email.parser import BytesParser

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """Process uploaded documents with LLM categorization."""
    
    def __init__(self, llm_manager, storage_path: str = "/app/data"):
        self.llm_manager = llm_manager
        self.storage_path = storage_path
        self.documents_db = {}  # In production, use real database
        
        # Create storage directories
        os.makedirs(os.path.join(storage_path, "uploads"), exist_ok=True)
        os.makedirs(os.path.join(storage_path, "processed"), exist_ok=True)
    
    async def process_upload(self, 
                           file_content: bytes,
                           filename: str,
                           metadata: Dict,
                           client_id: str) -> Dict:
        """Process uploaded document."""
        try:
            # Generate unique IDs
            upload_id = f"upload_{uuid.uuid4().hex[:12]}"
            document_id = f"doc_{uuid.uuid4().hex[:12]}"
            
            # Save uploaded file
            upload_path = os.path.join(self.storage_path, "uploads", f"{upload_id}_{filename}")
            with open(upload_path, 'wb') as f:
                f.write(file_content)
            
            # Calculate content hash
            content_hash = hashlib.sha256(file_content).hexdigest()
            
            # Extract text content
            text_content = await self._extract_text_content(upload_path, filename)
            
            if not text_content:
                raise Exception("Failed to extract text content from document")
            
            # Categorize using LLM
            categorization = self.llm_manager.categorize_document(text_content, filename)
            
            # Store processed content
            processed_path = os.path.join(self.storage_path, "processed", f"{document_id}.json")
            processed_data = {
                "document_id": document_id,
                "text_content": text_content[:50000],  # Limit stored text
                "categorization": categorization,
                "metadata": metadata
            }
            
            with open(processed_path, 'w') as f:
                json.dump(processed_data, f)
            
            # Create document record
            document = {
                "document_id": document_id,
                "upload_id": upload_id,
                "filename": filename,
                "file_type": self._detect_file_type(filename),
                "file_size": len(file_content),
                "status": "completed",
                "upload_date": datetime.utcnow().isoformat(),
                "processing_date": datetime.utcnow().isoformat(),
                "metadata": metadata,
                "categorization": categorization,
                "content_hash": content_hash,
                "storage_path": processed_path,
                "client_id": client_id
            }
            
            # Store in database
            self.documents_db[document_id] = document
            
            logger.info(f"Document processed successfully: {document_id}")
            
            return {
                "status": "completed",
                "upload_id": upload_id,
                "document_id": document_id,
                "categorization": categorization,
                "processing_time": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Document processing failed: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "upload_id": upload_id if 'upload_id' in locals() else None,
                "processing_time": datetime.utcnow().isoformat()
            }
    
    async def _extract_text_content(self, file_path: str, filename: str) -> str:
        """Extract text content from various file types."""
        file_ext = filename.lower().split('.')[-1]
        
        try:
            if file_ext == 'pdf':
                return self._extract_pdf_text(file_path)
            elif file_ext in ['docx', 'doc']:
                return self._extract_word_text(file_path)
            elif file_ext in ['xlsx', 'xls']:
                return self._extract_excel_text(file_path)
            elif file_ext == 'csv':
                return self._extract_csv_text(file_path)
            elif file_ext == 'txt':
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    return f.read()
            elif file_ext in ['eml', 'msg']:
                return self._extract_email_text(file_path)
            else:
                # Try to read as text
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    return f.read()
                    
        except Exception as e:
            logger.error(f"Failed to extract text from {filename}: {e}")
            return ""
    
    def _extract_pdf_text(self, file_path: str) -> str:
        """Extract text from PDF."""
        text_content = ""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page_num, page in enumerate(pdf_reader.pages):
                    if page_num > 50:  # Limit pages for performance
                        break
                    text_content += page.extract_text() + "\n"
        except Exception as e:
            logger.error(f"PDF extraction error: {e}")
        
        return text_content
    
    def _extract_word_text(self, file_path: str) -> str:
        """Extract text from Word document."""
        text_content = ""
        try:
            doc = DocxDocument(file_path)
            for paragraph in doc.paragraphs[:1000]:  # Limit paragraphs
                text_content += paragraph.text + "\n"
        except Exception as e:
            logger.error(f"Word extraction error: {e}")
        
        return text_content
    
    def _extract_excel_text(self, file_path: str) -> str:
        """Extract text from Excel file."""
        text_content = ""
        try:
            # Read all sheets
            excel_file = pd.ExcelFile(file_path)
            for sheet_name in excel_file.sheet_names[:5]:  # Limit sheets
                df = pd.read_excel(file_path, sheet_name=sheet_name, nrows=1000)
                text_content += f"Sheet: {sheet_name}\n"
                text_content += df.to_string(max_rows=100) + "\n\n"
        except Exception as e:
            logger.error(f"Excel extraction error: {e}")
        
        return text_content
    
    def _extract_csv_text(self, file_path: str) -> str:
        """Extract text from CSV file."""
        text_content = ""
        try:
            df = pd.read_csv(file_path, nrows=1000)
            text_content = df.to_string(max_rows=100)
        except Exception as e:
            logger.error(f"CSV extraction error: {e}")
        
        return text_content
    
    def _extract_email_text(self, file_path: str) -> str:
        """Extract text from email file."""
        text_content = ""
        try:
            with open(file_path, 'rb') as f:
                msg = BytesParser(policy=policy.default).parse(f)
            
            # Extract headers
            text_content += f"From: {msg.get('From', 'Unknown')}\n"
            text_content += f"To: {msg.get('To', 'Unknown')}\n"
            text_content += f"Subject: {msg.get('Subject', 'No Subject')}\n"
            text_content += f"Date: {msg.get('Date', 'Unknown')}\n\n"
            
            # Extract body
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == 'text/plain':
                        text_content += part.get_content() + "\n"
            else:
                text_content += msg.get_content()
                
        except Exception as e:
            logger.error(f"Email extraction error: {e}")
        
        return text_content
    
    def _detect_file_type(self, filename: str) -> str:
        """Detect file type from filename."""
        ext = filename.lower().split('.')[-1]
        type_map = {
            'pdf': 'pdf',
            'docx': 'word',
            'doc': 'word',
            'xlsx': 'excel',
            'xls': 'excel',
            'csv': 'csv',
            'txt': 'text',
            'eml': 'email',
            'msg': 'email'
        }
        return type_map.get(ext, 'other')
    
    def get_document(self, document_id: str) -> Optional[Dict]:
        """Get document by ID."""
        return self.documents_db.get(document_id)
    
    def search_documents(self, client_id: str, filters: Dict) -> List[Dict]:
        """Search documents with filters."""
        results = []
        
        for doc in self.documents_db.values():
            if doc['client_id'] != client_id:
                continue
            
            # Apply filters
            if filters.get('department'):
                if doc['categorization']['department'] != filters['department']:
                    continue
            
            if filters.get('document_type'):
                if doc['categorization']['document_type'] != filters['document_type']:
                    continue
            
            if filters.get('date_from'):
                if doc['upload_date'] < filters['date_from']:
                    continue
            
            if filters.get('date_to'):
                if doc['upload_date'] > filters['date_to']:
                    continue
            
            results.append(doc)
        
        return results