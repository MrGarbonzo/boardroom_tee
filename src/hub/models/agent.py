"""Agent models for Hub."""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime
from enum import Enum


class AgentStatus(str, Enum):
    """Agent status."""
    VERIFIED = "verified"
    UNVERIFIED = "unverified"
    INACTIVE = "inactive"
    FAILED = "failed"


class AgentCapability(str, Enum):
    """Standard agent capabilities."""
    FINANCIAL_ANALYSIS = "financial_analysis"
    ROI_CALCULATION = "roi_calculation"
    BUDGET_PLANNING = "budget_planning"
    VARIANCE_ANALYSIS = "variance_analysis"
    CASH_FLOW_ANALYSIS = "cash_flow_analysis"
    RISK_ASSESSMENT = "risk_assessment"
    MARKETING_ANALYSIS = "marketing_analysis"
    CAMPAIGN_PERFORMANCE = "campaign_performance"
    CUSTOMER_SEGMENTATION = "customer_segmentation"
    MARKET_RESEARCH = "market_research"
    SALES_FORECASTING = "sales_forecasting"
    PIPELINE_ANALYSIS = "pipeline_analysis"


class AgentRegistration(BaseModel):
    """Agent registration request."""
    agent_id: str
    agent_type: str
    capabilities: List[str]
    endpoint: str
    attestation_endpoint: str
    attestation_data: Dict


class Agent(BaseModel):
    """Registered agent model."""
    agent_id: str
    agent_type: str
    capabilities: List[str]
    endpoint: str
    attestation_endpoint: str
    public_key: str
    attestation_quote: str
    status: AgentStatus
    registered_at: datetime
    last_seen: datetime
    client_id: str
    measurements: Dict = Field(default_factory=dict)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }