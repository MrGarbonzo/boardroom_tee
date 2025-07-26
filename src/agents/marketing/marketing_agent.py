"""Marketing Agent - Specialized marketing intelligence agent."""

import os
import logging
import sys
from typing import Dict, List

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from agents.base_agent import BaseAgent
from agents.marketing.services import MarketingLLM, CampaignAnalyzer

logger = logging.getLogger(__name__)


class MarketingAgent(BaseAgent):
    """Specialized marketing agent for campaign analysis and marketing intelligence."""
    
    def __init__(self, agent_id: str = None, client_id: str = None):
        # Generate agent ID if not provided
        if not agent_id:
            client_id = client_id or os.getenv('CLIENT_ID', 'default')
            agent_id = f"marketing-agent-{client_id}"
        
        # Define capabilities
        capabilities = [
            "marketing_analysis",
            "campaign_performance",
            "customer_segmentation",
            "market_research",
            "roi_analysis",
            "optimization_recommendations"
        ]
        
        # Initialize base agent
        super().__init__(agent_id, "marketing", capabilities)
        
        # Initialize marketing-specific services
        self.marketing_llm = MarketingLLM()
        self.campaign_analyzer = CampaignAnalyzer(self.marketing_llm)
        
    async def initialize(self):
        """Initialize the marketing agent."""
        try:
            # Initialize base agent
            await super().initialize()
            
            # Load marketing model
            await self.marketing_llm.load_model()
            
            # Register marketing-specific handlers
            self.register_marketing_handlers()
            
            logger.info("Marketing agent initialized successfully")
            
        except Exception as e:
            logger.error(f"Marketing agent initialization failed: {e}")
            raise
    
    def register_marketing_handlers(self):
        """Register marketing-specific request handlers."""
        # Campaign analysis handler
        self.register_handler("campaign_analysis", self.handle_campaign_analysis)
        
        # ROI collaboration handler
        self.register_handler("roi_collaboration", self.handle_roi_collaboration)
        
        # Campaign optimization handler
        self.register_handler("campaign_optimization", self.handle_campaign_optimization)
        
        # Customer segmentation handler
        self.register_handler("customer_segmentation", self.handle_customer_segmentation)
        
        # Market research handler
        self.register_handler("market_research", self.handle_market_research)
    
    async def process_collaboration_request(self,
                                          task_description: str,
                                          context: Dict,
                                          data_package: Dict) -> Dict:
        """Process collaboration request from other agents."""
        try:
            task_lower = task_description.lower()
            
            # Route to appropriate analysis based on task
            if 'roi' in task_lower or 'return' in task_lower or 'financial' in task_lower:
                return await self.handle_roi_collaboration_request(task_description, context, data_package)
            elif 'campaign' in task_lower or 'performance' in task_lower:
                return await self.handle_campaign_collaboration(task_description, context, data_package)
            elif 'optimization' in task_lower or 'improve' in task_lower:
                return await self.handle_optimization_collaboration(task_description, context, data_package)
            elif 'customer' in task_lower or 'segment' in task_lower:
                return await self.handle_customer_collaboration(task_description, context, data_package)
            else:
                # General marketing analysis
                return await self.handle_general_marketing_analysis(task_description, context, data_package)
                
        except Exception as e:
            logger.error(f"Collaboration request processing failed: {e}")
            return {
                "error": f"Processing failed: {str(e)}",
                "task": task_description,
                "agent_id": self.agent_id
            }
    
    async def handle_roi_collaboration_request(self, task: str, context: Dict, data_package: Dict) -> Dict:
        """Handle ROI collaboration requests with finance agent."""
        logger.info(f"Processing ROI collaboration: {task}")
        
        # Prepare request data
        request_data = {
            "task_description": task,
            "context": context,
            "data_package": data_package,
            "analysis_type": "roi_collaboration"
        }
        
        # Perform ROI analysis from marketing perspective
        result = await self.campaign_analyzer.roi_collaboration_analysis(request_data)
        
        # Format for collaboration response
        return {
            "analysis_type": "marketing_roi",
            "summary": f"Marketing ROI Analysis: {result.get('marketing_roi_metrics', {}).get('immediate_roi', 'N/A')}% immediate ROI",
            "detailed_results": result,
            "key_insights": result.get('collaboration_recommendations', [])[:3],
            "finance_collaboration_data": result.get('finance_collaboration_data', {}),
            "confidence_score": result.get('confidence_score', 0.87),
            "collaboration_successful": True
        }
    
    async def handle_campaign_collaboration(self, task: str, context: Dict, data_package: Dict) -> Dict:
        """Handle campaign performance collaboration requests."""
        logger.info(f"Processing campaign collaboration: {task}")
        
        result = await self.campaign_analyzer.comprehensive_campaign_analysis(data_package)
        
        return {
            "analysis_type": "campaign_performance",
            "summary": f"Campaign Analysis: {result.get('campaign_overview', {}).get('name', 'Campaign')} performance assessment",
            "detailed_results": result,
            "key_insights": result.get('combined_insights', {}).get('optimization_opportunities', [])[:3],
            "confidence_score": result.get('confidence_score', 0.89),
            "collaboration_successful": True
        }
    
    async def handle_optimization_collaboration(self, task: str, context: Dict, data_package: Dict) -> Dict:
        """Handle campaign optimization collaboration."""
        logger.info(f"Processing optimization collaboration: {task}")
        
        request_data = {
            "context": context,
            "data_package": data_package
        }
        
        result = await self.campaign_analyzer.campaign_optimization_analysis(request_data)
        
        return {
            "analysis_type": "campaign_optimization",
            "summary": f"Optimization Analysis: {len(result.get('priority_actions', []))} priority actions identified",
            "detailed_results": result,
            "key_insights": result.get('priority_actions', [])[:3],
            "expected_impact": result.get('expected_impact', {}),
            "confidence_score": result.get('confidence_score', 0.89),
            "collaboration_successful": True
        }
    
    async def handle_customer_collaboration(self, task: str, context: Dict, data_package: Dict) -> Dict:
        """Handle customer segmentation collaboration."""
        logger.info(f"Processing customer collaboration: {task}")
        
        # Extract customer data
        customer_data = data_package.get('customer_data', context)
        
        # Use LLM for segmentation analysis
        segmentation_result = self.marketing_llm.analyze_customer_segmentation(customer_data)
        
        return {
            "analysis_type": "customer_segmentation",
            "summary": f"Segmentation Analysis: {segmentation_result.get('segmentation_analysis', {}).get('segments_identified', 0)} segments identified",
            "detailed_results": segmentation_result,
            "key_insights": segmentation_result.get('targeting_recommendations', [])[:3],
            "confidence_score": segmentation_result.get('confidence_score', 0.85),
            "collaboration_successful": True
        }
    
    async def handle_general_marketing_analysis(self, task: str, context: Dict, data_package: Dict) -> Dict:
        """Handle general marketing analysis requests."""
        logger.info(f"Processing general marketing analysis: {task}")
        
        # Use LLM for general analysis
        campaign_data = self._extract_campaign_data_from_package(data_package, context)
        analysis_result = self.marketing_llm.analyze_campaign_performance(campaign_data, task)
        
        return {
            "analysis_type": "general_marketing",
            "summary": analysis_result.get('campaign_summary', 'Marketing analysis completed'),
            "detailed_results": analysis_result,
            "key_insights": analysis_result.get('recommendations', [])[:3],
            "confidence_score": analysis_result.get('confidence_score', 0.85),
            "collaboration_successful": True
        }
    
    # Direct handler methods for API endpoints
    async def handle_campaign_analysis(self, payload: Dict) -> Dict:
        """Handle direct campaign analysis request."""
        return await self.campaign_analyzer.comprehensive_campaign_analysis(payload)
    
    async def handle_roi_collaboration(self, payload: Dict) -> Dict:
        """Handle direct ROI collaboration request."""
        return await self.campaign_analyzer.roi_collaboration_analysis(payload)
    
    async def handle_campaign_optimization(self, payload: Dict) -> Dict:
        """Handle direct campaign optimization request."""
        return await self.campaign_analyzer.campaign_optimization_analysis(payload)
    
    async def handle_customer_segmentation(self, payload: Dict) -> Dict:
        """Handle customer segmentation request."""
        customer_data = payload.get('customer_data', payload.get('context', {}))
        result = self.marketing_llm.analyze_customer_segmentation(customer_data)
        
        return {
            "analysis_type": "customer_segmentation",
            "result": result,
            "agent_id": self.agent_id,
            "processing_time_ms": 1800  # Mock processing time
        }
    
    async def handle_market_research(self, payload: Dict) -> Dict:
        """Handle market research request."""
        market_data = payload.get('market_data', payload.get('context', {}))
        result = self.marketing_llm.analyze_market_trends(market_data)
        
        return {
            "analysis_type": "market_research",
            "result": result,
            "agent_id": self.agent_id,
            "processing_time_ms": 2200  # Mock processing time
        }
    
    async def collaborate_with_finance(self, campaign_data: Dict) -> Dict:
        """Collaborate with finance agent for ROI analysis."""
        try:
            result = await self.collaborate_with_agent(
                target_agent_type="finance",
                task_description="Analyze marketing campaign ROI and financial impact",
                context=campaign_data,
                data_requirements=["financial_data", "roi_calculations"]
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Finance collaboration failed: {e}")
            return {"error": str(e)}
    
    def _extract_campaign_data_from_package(self, data_package: Dict, context: Dict) -> Dict:
        """Extract campaign data from data package and context."""
        campaign_data = {}
        
        # Extract from context
        campaign_data.update(context)
        
        # Extract from data package
        if "marketing_data" in data_package:
            campaign_data.update(data_package["marketing_data"])
        
        # Extract from nested data
        data = data_package.get("data", {})
        if "marketing_data" in data:
            campaign_data.update(data["marketing_data"])
        
        return campaign_data
    
    def get_specialization_info(self) -> Dict:
        """Get marketing agent specialization information."""
        return {
            "agent_type": "marketing",
            "model": "mistralai/Mistral-7B-Instruct-v0.3",
            "specializations": [
                "Campaign Performance Analysis",
                "Marketing ROI Calculation",
                "Customer Segmentation",
                "Campaign Optimization",
                "Market Research",
                "Cross-Channel Attribution"
            ],
            "collaboration_capabilities": [
                "Finance ROI collaboration",
                "Customer lifetime value analysis",
                "Cross-departmental attribution modeling"
            ],
            "data_types": [
                "Campaign performance data",
                "Customer behavioral data",
                "Market research data",
                "Ad spend and attribution data",
                "Conversion metrics"
            ]
        }