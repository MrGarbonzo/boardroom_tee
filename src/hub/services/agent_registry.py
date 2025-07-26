"""Agent registry service for Hub."""

import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)


class AgentRegistry:
    """Manage agent registration and discovery with attestation verification."""
    
    def __init__(self, attestation_client):
        self.attestation_client = attestation_client
        self.agents = {}  # agent_id -> agent_data
        self.client_agents = {}  # client_id -> [agent_ids]
        
    async def register_agent(self, registration_data: Dict, client_id: str) -> Dict:
        """Register a new agent with attestation verification."""
        try:
            agent_id = registration_data["agent_id"]
            
            # Verify attestation
            attestation_data = registration_data.get("attestation_data", {})
            quote = attestation_data.get("quote")
            public_key = attestation_data.get("public_key")
            
            if not quote or not public_key:
                return {
                    "status": "rejected",
                    "verification_status": "failed",
                    "error": "Missing attestation data"
                }
            
            # Verify attestation quote
            verified, verification_result = self.attestation_client.verify_attestation_quote(quote)
            
            if not verified:
                return {
                    "status": "rejected",
                    "verification_status": "failed",
                    "error": verification_result.get("error", "Attestation verification failed")
                }
            
            # Create agent record
            agent = {
                "agent_id": agent_id,
                "agent_type": registration_data["agent_type"],
                "capabilities": registration_data["capabilities"],
                "endpoint": registration_data["endpoint"],
                "attestation_endpoint": registration_data["attestation_endpoint"],
                "public_key": public_key,
                "attestation_quote": quote,
                "status": "verified",
                "registered_at": datetime.utcnow().isoformat(),
                "last_seen": datetime.utcnow().isoformat(),
                "client_id": client_id,
                "measurements": verification_result.get("measurements", {})
            }
            
            # Store agent
            self.agents[agent_id] = agent
            
            # Track by client
            if client_id not in self.client_agents:
                self.client_agents[client_id] = []
            self.client_agents[client_id].append(agent_id)
            
            logger.info(f"Agent {agent_id} registered successfully for client {client_id}")
            
            return {
                "status": "registered",
                "verification_status": "verified",
                "agent_id": agent_id,
                "measurements": agent["measurements"]
            }
            
        except Exception as e:
            logger.error(f"Agent registration failed: {e}")
            return {
                "status": "rejected",
                "verification_status": "failed",
                "error": str(e)
            }
    
    def get_agent(self, agent_id: str, client_id: str) -> Optional[Dict]:
        """Get agent by ID for specific client."""
        agent = self.agents.get(agent_id)
        if agent and agent["client_id"] == client_id:
            return agent
        return None
    
    def get_agents_by_capability(self, capability: str, client_id: str) -> List[Dict]:
        """Get agents with specific capability for client."""
        results = []
        
        for agent_id in self.client_agents.get(client_id, []):
            agent = self.agents.get(agent_id)
            if agent and capability in agent["capabilities"] and agent["status"] == "verified":
                results.append(agent)
        
        return results
    
    def get_all_agents(self, client_id: str) -> List[Dict]:
        """Get all agents for specific client."""
        results = []
        
        for agent_id in self.client_agents.get(client_id, []):
            agent = self.agents.get(agent_id)
            if agent:
                results.append(agent)
        
        return results
    
    def update_agent_heartbeat(self, agent_id: str, client_id: str) -> bool:
        """Update agent last seen timestamp."""
        agent = self.get_agent(agent_id, client_id)
        if agent:
            agent["last_seen"] = datetime.utcnow().isoformat()
            return True
        return False
    
    def check_agent_health(self, client_id: str) -> Dict:
        """Check health status of all agents for client."""
        health_status = {
            "healthy": [],
            "unhealthy": [],
            "inactive": []
        }
        
        current_time = datetime.utcnow()
        
        for agent_id in self.client_agents.get(client_id, []):
            agent = self.agents.get(agent_id)
            if not agent:
                continue
            
            # Parse last seen time
            last_seen = datetime.fromisoformat(agent["last_seen"])
            time_since_seen = current_time - last_seen
            
            if time_since_seen < timedelta(minutes=5):
                health_status["healthy"].append({
                    "agent_id": agent_id,
                    "agent_type": agent["agent_type"],
                    "last_seen": agent["last_seen"]
                })
            elif time_since_seen < timedelta(minutes=15):
                health_status["unhealthy"].append({
                    "agent_id": agent_id,
                    "agent_type": agent["agent_type"],
                    "last_seen": agent["last_seen"]
                })
            else:
                health_status["inactive"].append({
                    "agent_id": agent_id,
                    "agent_type": agent["agent_type"],
                    "last_seen": agent["last_seen"]
                })
                # Update agent status
                agent["status"] = "inactive"
        
        return health_status
    
    def remove_agent(self, agent_id: str, client_id: str) -> bool:
        """Remove agent from registry."""
        agent = self.get_agent(agent_id, client_id)
        if agent:
            del self.agents[agent_id]
            self.client_agents[client_id].remove(agent_id)
            logger.info(f"Agent {agent_id} removed from registry")
            return True
        return False
    
    def get_agent_directory(self, client_id: str) -> List[Dict]:
        """Get simplified agent directory for client."""
        directory = []
        
        for agent_id in self.client_agents.get(client_id, []):
            agent = self.agents.get(agent_id)
            if agent and agent["status"] == "verified":
                directory.append({
                    "agent_id": agent_id,
                    "agent_type": agent["agent_type"],
                    "capabilities": agent["capabilities"],
                    "endpoint": agent["endpoint"],
                    "status": "online" if self._is_agent_online(agent) else "offline"
                })
        
        return directory
    
    def _is_agent_online(self, agent: Dict) -> bool:
        """Check if agent is considered online."""
        try:
            last_seen = datetime.fromisoformat(agent["last_seen"])
            return (datetime.utcnow() - last_seen) < timedelta(minutes=5)
        except:
            return False