"""Orchestration models for Hub."""

from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from datetime import datetime


class OrchestrationRequest(BaseModel):
    """Orchestration request from client or agent."""
    query: str
    requesting_agent: Optional[str] = None
    context: Dict = Field(default_factory=dict)
    data_requirements: List[str] = Field(default_factory=list)
    priority: str = "normal"
    timeout_seconds: int = 60


class OrchestrationResponse(BaseModel):
    """Orchestration response."""
    routing_id: str
    target_agent: str
    reasoning: str
    estimated_time_minutes: int
    data_package: Optional[Dict] = None
    routed_at: datetime
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }