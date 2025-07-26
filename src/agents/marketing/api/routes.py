"""Marketing agent API routes."""

import logging
from fastapi import APIRouter, HTTPException, Header
from typing import Dict, Optional
import os

logger = logging.getLogger(__name__)

router = APIRouter()

# Global service references (set by main.py)
_marketing_agent = None
_campaign_analyzer = None


def set_services(marketing_agent, campaign_analyzer):
    """Set service dependencies."""
    global _marketing_agent, _campaign_analyzer
    _marketing_agent = marketing_agent
    _campaign_analyzer = campaign_analyzer


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
            result = await _marketing_agent.handle_collaboration_request(request_data)
            return result
        elif request_type == "campaign_analysis":
            # Specific campaign analysis request
            result = await _campaign_analyzer.comprehensive_campaign_analysis(request_data)
            return result
        elif request_type == "roi_collaboration":
            # ROI collaboration with finance
            result = await _campaign_analyzer.roi_collaboration_analysis(request_data)
            return result
        elif request_type == "campaign_optimization":
            # Campaign optimization analysis
            result = await _campaign_analyzer.campaign_optimization_analysis(request_data)
            return result
        else:
            # General marketing analysis
            result = await _campaign_analyzer.comprehensive_campaign_analysis(request_data)
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
        result = await _marketing_agent.communication.handle_collaboration_request(secure_message)
        return result
        
    except Exception as e:
        logger.error(f"Collaboration handling failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/capabilities")
async def get_capabilities():
    """Get agent capabilities."""
    return {
        "agent_id": _marketing_agent.agent_id if _marketing_agent else "marketing-agent",
        "agent_type": "marketing",
        "capabilities": [
            "marketing_analysis",
            "campaign_performance",
            "customer_segmentation",
            "market_research",
            "roi_analysis",
            "optimization_recommendations"
        ],
        "specializations": [
            "Campaign Performance Analysis",
            "Marketing ROI Calculation",
            "Customer Segmentation Analysis",
            "Campaign Optimization",
            "Market Trend Analysis",
            "Cross-Channel Attribution"
        ],
        "collaboration_types": [
            "roi_collaboration",
            "campaign_optimization",
            "customer_insights"
        ]
    }


@router.get("/health")
async def health_check():
    """Agent health check."""
    try:
        if not _marketing_agent:
            return {"status": "unhealthy", "error": "Agent not initialized"}
        
        # Get agent health info
        health_info = await _marketing_agent.handle_health_check({})
        
        # Add marketing-specific health metrics
        health_info.update({
            "model_status": "loaded" if _marketing_agent.marketing_llm.is_loaded else "unloaded",
            "memory_usage": _marketing_agent.marketing_llm.get_memory_usage(),
            "analysis_capabilities": "operational",
            "last_analysis": "2024-01-01T00:00:00Z"  # Would track real last analysis
        })
        
        return health_info
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "agent_type": "marketing"
        }


@router.get("/metrics")
async def get_metrics():
    """Get agent performance metrics."""
    return {
        "campaigns_analyzed": 89,  # Mock metrics
        "average_response_time_ms": 2200,
        "accuracy_score": 0.91,
        "uptime_hours": 36.2,
        "collaboration_requests": 32,
        "model_performance": {
            "confidence_scores": {
                "average": 0.89,
                "min": 0.72,
                "max": 0.96
            },
            "analysis_types": {
                "campaign_performance": "1.8s",
                "roi_collaboration": "2.4s",
                "optimization": "2.9s"
            }
        }
    }


@router.post("/campaign/analyze")
async def analyze_campaign(campaign_data: Dict):
    """Analyze specific campaign performance."""
    try:
        request_data = {
            "type": "campaign_analysis",
            "context": campaign_data,
            "data_package": {"marketing_data": campaign_data}
        }
        
        result = await _campaign_analyzer.comprehensive_campaign_analysis(request_data)
        return result
        
    except Exception as e:
        logger.error(f"Campaign analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/campaign/optimize")
async def optimize_campaign(optimization_request: Dict):
    """Get campaign optimization recommendations."""
    try:
        request_data = {
            "type": "campaign_optimization",
            "context": optimization_request,
            "data_package": {"marketing_data": optimization_request}
        }
        
        result = await _campaign_analyzer.campaign_optimization_analysis(request_data)
        return result
        
    except Exception as e:
        logger.error(f"Campaign optimization failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))