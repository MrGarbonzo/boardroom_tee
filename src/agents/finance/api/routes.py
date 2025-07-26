"""Finance agent API routes."""

import logging
from fastapi import APIRouter, HTTPException, Header
from typing import Dict, Optional
import os

logger = logging.getLogger(__name__)

router = APIRouter()

# Global service references (set by main.py)
_finance_agent = None
_financial_analyzer = None


def set_services(finance_agent, financial_analyzer):
    """Set service dependencies."""
    global _finance_agent, _financial_analyzer
    _finance_agent = finance_agent
    _financial_analyzer = financial_analyzer


@router.post("/process")
async def process_request(
    request_data: Dict,
    x_hub_request: Optional[str] = Header(None),
    x_client_id: Optional[str] = Header(None)
):
    """Process analysis request from hub or other agents."""
    try:
        request_type = request_data.get("type", "general")
        
        if request_type == "collaboration_request":
            # Handle collaboration from other agents
            result = await _finance_agent.handle_collaboration_request(request_data)
            return result
        elif request_type == "roi_analysis":
            # Specific ROI analysis request
            result = await _financial_analyzer.roi_collaboration_analysis(request_data)
            return result
        elif request_type == "budget_variance":
            # Budget variance analysis
            result = await _financial_analyzer.budget_variance_analysis(request_data)
            return result
        else:
            # General financial analysis
            result = await _financial_analyzer.comprehensive_financial_analysis(request_data)
            return result
            
    except Exception as e:
        logger.error(f"Request processing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/collaborate")
async def handle_collaboration(
    secure_message: Dict,
    x_agent_id: Optional[str] = Header(None)
):
    """Handle collaboration request from another agent."""
    try:
        # Process secure message through agent communication
        result = await _finance_agent.communication.handle_collaboration_request(secure_message)
        return result
        
    except Exception as e:
        logger.error(f"Collaboration handling failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/capabilities")
async def get_capabilities():
    """Get agent capabilities."""
    return {
        "agent_id": _finance_agent.agent_id if _finance_agent else "finance-agent",
        "agent_type": "finance",
        "capabilities": [
            "financial_analysis",
            "roi_calculation",
            "budget_planning",
            "variance_analysis",
            "cash_flow_analysis",
            "risk_assessment"
        ],
        "specializations": [
            "Campaign ROI Analysis",
            "Budget Variance Analysis",
            "Financial Health Assessment",
            "Investment Analysis",
            "Cost-Benefit Analysis"
        ],
        "collaboration_types": [
            "roi_collaboration",
            "budget_variance",
            "financial_modeling"
        ]
    }


@router.get("/health")
async def health_check():
    """Agent health check."""
    try:
        if not _finance_agent:
            return {"status": "unhealthy", "error": "Agent not initialized"}
        
        # Get agent health info
        health_info = await _finance_agent.handle_health_check({})
        
        # Add finance-specific health metrics
        health_info.update({
            "model_status": "loaded" if _finance_agent.finance_llm.is_loaded else "unloaded",
            "memory_usage": _finance_agent.finance_llm.get_memory_usage(),
            "analysis_capabilities": "operational",
            "last_analysis": "2024-01-01T00:00:00Z"  # Would track real last analysis
        })
        
        return health_info
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "agent_type": "finance"
        }


@router.get("/metrics")
async def get_metrics():
    """Get agent performance metrics."""
    return {
        "analyses_completed": 150,  # Mock metrics
        "average_response_time_ms": 2500,
        "accuracy_score": 0.92,
        "uptime_hours": 24.5,
        "collaboration_requests": 45,
        "model_performance": {
            "confidence_scores": {
                "average": 0.87,
                "min": 0.65,
                "max": 0.98
            },
            "processing_times": {
                "roi_analysis": "2.1s",
                "budget_variance": "1.8s",
                "comprehensive": "3.2s"
            }
        }
    }