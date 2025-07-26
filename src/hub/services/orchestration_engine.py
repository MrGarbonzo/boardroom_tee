"""Orchestration engine for agent collaboration."""

import logging
import uuid
from typing import Dict, List, Optional
from datetime import datetime
import json

logger = logging.getLogger(__name__)


class OrchestrationEngine:
    """Orchestrate agent collaboration and data routing."""
    
    def __init__(self, llm_manager, agent_registry, vm_communication_manager):
        self.llm_manager = llm_manager
        self.agent_registry = agent_registry
        self.vm_communication = vm_communication_manager
        self.active_requests = {}  # routing_id -> request_data
        
    async def route_request(self, request_data: Dict, client_id: str) -> Dict:
        """Route collaboration request to best available agent."""
        try:
            query = request_data.get("query", "")
            requesting_agent = request_data.get("requesting_agent")
            context = request_data.get("context", {})
            data_requirements = request_data.get("data_requirements", [])
            
            # Get available agents for this client
            available_agents = self.agent_registry.get_all_agents(client_id)
            
            # Filter out requesting agent and inactive agents
            available_agents = [
                agent for agent in available_agents
                if agent["agent_id"] != requesting_agent and agent["status"] == "verified"
            ]
            
            if not available_agents:
                return {
                    "error": "No verified agents available for collaboration",
                    "available_agents": 0
                }
            
            # Use LLM to determine best agent
            routing_decision = self.llm_manager.route_to_agent(query, available_agents)
            
            # Find target agent
            target_agent = None
            for agent in available_agents:
                if agent["agent_type"] == routing_decision["best_agent"]:
                    target_agent = agent
                    break
            
            if not target_agent:
                # Fallback to first available agent
                target_agent = available_agents[0]
                routing_decision["reasoning"] = "Primary agent not found, using fallback"
            
            # Generate routing ID
            routing_id = f"route_{uuid.uuid4().hex[:8]}"
            
            # Prepare data package
            data_package = await self._prepare_data_package(
                request_data, target_agent, client_id
            )
            
            # Store active request
            self.active_requests[routing_id] = {
                "routing_id": routing_id,
                "request_data": request_data,
                "target_agent": target_agent,
                "client_id": client_id,
                "started_at": datetime.utcnow().isoformat()
            }
            
            # Send to target agent via VM communication
            collaboration_result = await self.vm_communication.send_to_agent(
                agent_type=target_agent["agent_type"],
                data={
                    "routing_id": routing_id,
                    "query": query,
                    "context": context,
                    "data_package": data_package,
                    "requesting_agent": requesting_agent,
                    "priority": routing_decision.get("priority", "normal")
                }
            )
            
            logger.info(f"Routed request {routing_id} to {target_agent['agent_type']}")
            
            return {
                "routing_id": routing_id,
                "target_agent": target_agent["agent_id"],
                "agent_type": target_agent["agent_type"],
                "reasoning": routing_decision["reasoning"],
                "estimated_time_minutes": routing_decision.get("estimated_time", 5),
                "data_package": {"size": len(json.dumps(data_package))},
                "routed_at": datetime.utcnow().isoformat(),
                "collaboration_result": collaboration_result
            }
            
        except Exception as e:
            logger.error(f"Request routing failed: {e}")
            return {
                "error": f"Routing failed: {str(e)}",
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def _prepare_data_package(self, 
                                  request_data: Dict,
                                  target_agent: Dict,
                                  client_id: str) -> Dict:
        """Prepare encrypted data package for target agent."""
        try:
            # Get relevant data based on requirements
            data_requirements = request_data.get("data_requirements", [])
            context = request_data.get("context", {})
            
            # In production, would fetch actual data from document store
            # For now, create mock data package
            relevant_data = {
                "client_id": client_id,
                "request_context": context,
                "data_types": data_requirements,
                "documents": []  # Would include relevant document IDs/content
            }
            
            # Add specific data based on requirements
            if "financial_data" in data_requirements:
                relevant_data["financial_data"] = {
                    "revenue": context.get("revenue", 1000000),
                    "expenses": context.get("expenses", 800000),
                    "period": context.get("period", "Q4 2024")
                }
            
            if "marketing_data" in data_requirements:
                relevant_data["marketing_data"] = {
                    "campaign_name": context.get("campaign_name", "Holiday Campaign"),
                    "spend": context.get("marketing_spend", 50000),
                    "impressions": context.get("impressions", 1000000)
                }
            
            # In production, would encrypt with target agent's public key
            # For now, return as-is
            return {
                "encrypted": False,
                "data": relevant_data,
                "prepared_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to prepare data package: {e}")
            return {"error": str(e)}
    
    async def process_collaboration_response(self, 
                                           routing_id: str,
                                           response_data: Dict) -> Dict:
        """Process response from collaborating agent."""
        try:
            # Get original request
            active_request = self.active_requests.get(routing_id)
            if not active_request:
                return {"error": "Unknown routing ID"}
            
            # Add to response history
            if "responses" not in active_request:
                active_request["responses"] = []
            
            active_request["responses"].append({
                "agent_id": response_data.get("agent_id"),
                "agent_type": response_data.get("agent_type"),
                "result": response_data.get("result"),
                "received_at": datetime.utcnow().isoformat()
            })
            
            # Check if we need more collaborations
            if self._needs_additional_collaboration(active_request, response_data):
                # Route to another agent
                next_agent = await self._determine_next_agent(active_request)
                if next_agent:
                    return await self.route_request(
                        active_request["request_data"],
                        active_request["client_id"]
                    )
            
            # Synthesize all responses
            all_responses = active_request.get("responses", [])
            synthesis = self.llm_manager.synthesize_results(all_responses)
            
            # Clean up
            del self.active_requests[routing_id]
            
            return {
                "routing_id": routing_id,
                "status": "completed",
                "synthesis": synthesis,
                "responses": all_responses,
                "completed_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to process collaboration response: {e}")
            return {"error": str(e)}
    
    def _needs_additional_collaboration(self, 
                                      active_request: Dict,
                                      response_data: Dict) -> bool:
        """Determine if additional collaboration is needed."""
        # Simple logic: if confidence is low, might need another opinion
        result = response_data.get("result", {})
        confidence = result.get("confidence_score", 1.0)
        
        # Only do one additional collaboration max
        responses = active_request.get("responses", [])
        if len(responses) >= 2:
            return False
        
        return confidence < 0.7
    
    async def _determine_next_agent(self, active_request: Dict) -> Optional[Dict]:
        """Determine next agent for collaboration."""
        # Get agents that haven't responded yet
        responded_agents = {
            r["agent_id"] for r in active_request.get("responses", [])
        }
        
        available_agents = self.agent_registry.get_all_agents(
            active_request["client_id"]
        )
        
        # Filter out agents that have already responded
        remaining_agents = [
            agent for agent in available_agents
            if agent["agent_id"] not in responded_agents
        ]
        
        if remaining_agents:
            return remaining_agents[0]
        
        return None
    
    def get_active_requests(self, client_id: str) -> List[Dict]:
        """Get active orchestration requests for client."""
        active = []
        
        for routing_id, request in self.active_requests.items():
            if request["client_id"] == client_id:
                active.append({
                    "routing_id": routing_id,
                    "target_agent": request["target_agent"]["agent_type"],
                    "started_at": request["started_at"],
                    "status": "active"
                })
        
        return active