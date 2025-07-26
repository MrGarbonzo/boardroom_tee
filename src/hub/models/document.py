"""Document models for Hub."""

from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from datetime import datetime
from enum import Enum


class DocumentStatus(str, Enum):
    """Document processing status."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class DocumentMetadata(BaseModel):
    """Document metadata."""
    department: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    user_metadata: Dict = Field(default_factory=dict)


class DocumentCategorization(BaseModel):
    """LLM-generated document categorization."""
    department: str
    document_type: str
    key_terms: List[str]
    time_period: Optional[str] = None
    summary: str
    confidence_score: float = Field(ge=0.0, le=1.0)


class Document(BaseModel):
    """Document model."""
    document_id: str
    upload_id: str
    filename: str
    file_type: str
    file_size: int
    status: DocumentStatus
    upload_date: datetime
    processing_date: Optional[datetime] = None
    metadata: DocumentMetadata
    categorization: Optional[DocumentCategorization] = None
    content_hash: str
    storage_path: str
    client_id: str
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }