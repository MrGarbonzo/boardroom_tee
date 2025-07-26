"""Finance Agent - Specialized financial analysis agent."""

import os
import logging
import sys
from typing import Dict, List

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from agents.base_agent import BaseAgent
from agents.finance.services import FinanceLLM, FinancialAnalyzer

logger = logging.getLogger(__name__)


class FinanceAgent(BaseAgent):
    """Specialized finance agent for financial analysis and ROI calculations."""
    
    def __init__(self, agent_id: str = None, client_id: str = None):
        # Generate agent ID if not provided
        if not agent_id:
            client_id = client_id or os.getenv('CLIENT_ID', 'default')
            agent_id = f"finance-agent-{client_id}"
        
        # Define capabilities
        capabilities = [
            "financial_analysis",
            "roi_calculation",
            "budget_planning",
            "variance_analysis",
            "cash_flow_analysis",
            "risk_assessment"
        ]
        
        # Initialize base agent
        super().__init__(agent_id, "finance", capabilities)
        
        # Initialize finance-specific services
        self.finance_llm = FinanceLLM()
        self.financial_analyzer = FinancialAnalyzer(self.finance_llm)
        
    async def initialize(self):
        """Initialize the finance agent."""
        try:
            # Initialize base agent
            await super().initialize()
            
            # Load finance model
            await self.finance_llm.load_model()
            
            # Register finance-specific handlers
            self.register_finance_handlers()
            
            logger.info("Finance agent initialized successfully")
            
        except Exception as e:
            logger.error(f"Finance agent initialization failed: {e}")
            raise
    
    def register_finance_handlers(self):
        """Register finance-specific request handlers."""
        # ROI analysis handler
        self.register_handler("roi_analysis", self.handle_roi_analysis)
        
        # Budget variance handler
        self.register_handler("budget_variance", self.handle_budget_variance)
        
        # Financial health assessment handler
        self.register_handler("financial_health", self.handle_financial_health)
        
        # Investment analysis handler
        self.register_handler("investment_analysis", self.handle_investment_analysis)
    
    async def process_collaboration_request(self,
                                          task_description: str,
                                          context: Dict,
                                          data_package: Dict) -> Dict:
        """Process collaboration request from other agents."""
        try:
            task_lower = task_description.lower()
            
            # Route to appropriate analysis based on task
            if 'roi' in task_lower or 'return on investment' in task_lower:
                return await self.handle_roi_collaboration(task_description, context, data_package)
            elif 'budget' in task_lower or 'variance' in task_lower:
                return await self.handle_budget_collaboration(task_description, context, data_package)
            elif 'financial health' in task_lower or 'financial analysis' in task_lower:
                return await self.handle_financial_health_collaboration(task_description, context, data_package)
            else:
                # General financial analysis
                return await self.handle_general_financial_analysis(task_description, context, data_package)
                
        except Exception as e:
            logger.error(f"Collaboration request processing failed: {e}")
            return {
                "error": f"Processing failed: {str(e)}",
                "task": task_description,
                "agent_id": self.agent_id
            }
    
    async def handle_roi_collaboration(self, task: str, context: Dict, data_package: Dict) -> Dict:
        """Handle ROI-specific collaboration requests."""
        logger.info(f"Processing ROI collaboration: {task}")
        
        # Prepare request data
        request_data = {
            "task_description": task,
            "context": context,
            "data_package": data_package,
            "analysis_type": "roi_collaboration"
        }
        
        # Perform ROI analysis
        result = await self.financial_analyzer.roi_collaboration_analysis(request_data)
        
        # Format for collaboration response
        return {
            "analysis_type": "roi_analysis",
            "summary": f"ROI Analysis: {result.get('roi_metrics', {}).get('roi_percentage', 'N/A')}% return",
            "detailed_results": result,
            "key_insights": result.get('recommendations', [])[:3],
            "confidence_score": result.get('confidence_score', 0.85),
            "collaboration_successful": True
        }
    
    async def handle_budget_collaboration(self, task: str, context: Dict, data_package: Dict) -> Dict:
        """Handle budget variance collaboration requests."""
        logger.info(f"Processing budget collaboration: {task}")
        
        request_data = {
            "task_description": task,
            "context": context,
            "data_package": data_package,
            "analysis_type": "budget_variance"
        }
        
        result = await self.financial_analyzer.budget_variance_analysis(request_data)
        
        return {
            "analysis_type": "budget_variance",
            "summary": f"Budget Analysis: {result.get('variance_analysis', {}).get('impact_assessment', {}).get('overall_performance', 'Analyzed')}",
            "detailed_results": result,
            "key_insights": result.get('variance_analysis', {}).get('corrective_actions', [])[:3],
            "confidence_score": result.get('confidence_score', 0.90),
            "collaboration_successful": True
        }
    
    async def handle_financial_health_collaboration(self, task: str, context: Dict, data_package: Dict) -> Dict:
        """Handle financial health assessment collaboration."""
        logger.info(f"Processing financial health collaboration: {task}")
        
        result = await self.financial_analyzer.comprehensive_financial_analysis(data_package)
        
        return {
            "analysis_type": "financial_health",
            "summary": f"Financial Health: {result.get('combined_insights', {}).get('key_findings', ['Assessment completed'])[0]}",
            "detailed_results": result,
            "key_insights": result.get('combined_insights', {}).get('action_items', [])[:3],
            "confidence_score": result.get('confidence_score', 0.85),
            "collaboration_successful": True
        }
    
    async def handle_general_financial_analysis(self, task: str, context: Dict, data_package: Dict) -> Dict:
        """Handle general financial analysis requests."""
        logger.info(f"Processing general financial analysis: {task}")
        
        # Use LLM for analysis
        analysis_result = self.finance_llm.analyze_financial_data(data_package, task)
        
        return {
            "analysis_type": "general_financial",
            "summary": analysis_result.get('financial_summary', 'Financial analysis completed'),
            "detailed_results": analysis_result,
            "key_insights": analysis_result.get('recommendations', [])[:3],
            "confidence_score": analysis_result.get('confidence_score', 0.85),
            "collaboration_successful": True
        }
    
    # Direct handler methods for API endpoints
    async def handle_roi_analysis(self, payload: Dict) -> Dict:
        """Handle direct ROI analysis request."""
        return await self.financial_analyzer.roi_collaboration_analysis(payload)
    
    async def handle_budget_variance(self, payload: Dict) -> Dict:
        """Handle direct budget variance request."""
        return await self.financial_analyzer.budget_variance_analysis(payload)
    
    async def handle_financial_health(self, payload: Dict) -> Dict:
        """Handle direct financial health request."""
        return await self.financial_analyzer.comprehensive_financial_analysis(payload)
    
    async def handle_investment_analysis(self, payload: Dict) -> Dict:
        """Handle investment analysis request."""
        # Extract investment data
        investment_data = payload.get('investment_data', {})
        revenue_data = payload.get('revenue_data', {})
        
        # Use LLM for analysis
        result = self.finance_llm.calculate_roi_analysis(investment_data, revenue_data)
        
        return {
            "analysis_type": "investment_analysis",
            "result": result,
            "agent_id": self.agent_id,
            "processing_time_ms": 2000  # Mock processing time
        }
    
    async def collaborate_with_marketing(self, campaign_data: Dict) -> Dict:
        """Collaborate with marketing agent for campaign analysis."""
        try:
            result = await self.collaborate_with_agent(
                target_agent_type="marketing",
                task_description="Analyze marketing campaign performance for ROI calculation",
                context=campaign_data,
                data_requirements=["marketing_data", "campaign_metrics"]
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Marketing collaboration failed: {e}")
            return {"error": str(e)}
    
    def get_specialization_info(self) -> Dict:
        """Get finance agent specialization information."""
        return {
            "agent_type": "finance",
            "model": "AdaptLLM/finance-LLM",
            "specializations": [
                "ROI Analysis",
                "Budget Planning",
                "Variance Analysis",
                "Cash Flow Analysis",
                "Risk Assessment",
                "Investment Analysis"
            ],
            "collaboration_capabilities": [
                "Marketing campaign ROI analysis",
                "Cross-departmental budget review",
                "Strategic financial planning"
            ],
            "data_types": [
                "Financial statements",
                "Budget data",
                "Investment records",
                "Revenue data",
                "Expense reports"
            ]
        }