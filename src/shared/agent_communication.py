"""Agent communication protocols for attestation-verified messaging."""

import aiohttp
import asyncio
import logging
import json
from typing import Dict, Optional, List, Callable
from datetime import datetime

logger = logging.getLogger(__name__)


class AgentCommunication:
    """Handle agent-to-agent and agent-to-hub communication."""
    
    def __init__(self, 
                 agent_id: str,
                 agent_type: str,
                 key_manager,
                 attestation_client,
                 secure_messaging):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.key_manager = key_manager
        self.attestation_client = attestation_client
        self.secure_messaging = secure_messaging
        self.registered_agents = {}
        self.hub_endpoint = None
        self.collaboration_handlers = {}
        
    async def register_with_hub(self, hub_endpoint: str, capabilities: List[str]) -> bool:
        """Register this agent with the hub."""
        try:
            self.hub_endpoint = hub_endpoint
            
            # Generate attestation quote
            attestation_data = self.attestation_client.generate_attestation_quote()
            
            # Prepare registration data
            registration_data = {
                "agent_id": self.agent_id,
                "agent_type": self.agent_type,
                "capabilities": capabilities,
                "endpoint": f"http://{self.agent_id}:{self._get_agent_port()}",
                "attestation_endpoint": f"http://{self.agent_id}:{self._get_attestation_port()}",
                "attestation_data": {
                    "quote": attestation_data["quote"],
                    "public_key": self.key_manager.get_public_key_pem()
                }
            }
            
            # Send registration request
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Content-Type": "application/json",
                    "X-Agent-ID": self.agent_id,
                    "X-Attestation-Quote": attestation_data["quote"],
                    "X-Public-Key": self.key_manager.get_public_key_pem()
                }
                
                async with session.post(
                    f"{hub_endpoint}/api/v1/agents/register",
                    json=registration_data,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 201:
                        result = await response.json()
                        logger.info(f"Agent {self.agent_id} registered successfully")
                        return result.get("verification_status") == "verified"
                    else:
                        error_text = await response.text()
                        logger.error(f"Registration failed: {response.status} - {error_text}")
                        return False
                        
        except Exception as e:
            logger.error(f"Failed to register with hub: {e}")
            return False
    
    async def discover_agents(self, capability: Optional[str] = None) -> List[Dict]:
        """Discover other agents via hub directory."""
        try:
            if not self.hub_endpoint:
                raise Exception("Not registered with hub")
            
            # Query hub directory
            params = {"capability": capability} if capability else {}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.hub_endpoint}/api/v1/agents/directory",
                    params=params,
                    headers={"X-Agent-ID": self.agent_id},
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        agents = await response.json()
                        
                        # Update local registry
                        for agent in agents:
                            self.registered_agents[agent["agent_id"]] = agent
                        
                        return agents
                    else:
                        logger.error(f"Failed to discover agents: {response.status}")
                        return []
                        
        except Exception as e:
            logger.error(f"Agent discovery failed: {e}")
            return []
    
    async def send_collaboration_request(self,
                                       target_agent_id: str,
                                       task_description: str,
                                       context: Dict,
                                       data_requirements: List[str]) -> Dict:
        """Send collaboration request to another agent."""
        try:
            # Get target agent info
            target_agent = self.registered_agents.get(target_agent_id)
            if not target_agent:
                # Try to discover
                await self.discover_agents()
                target_agent = self.registered_agents.get(target_agent_id)
                
                if not target_agent:
                    return {"error": f"Target agent {target_agent_id} not found"}
            
            # Create secure collaboration request
            secure_message = self.secure_messaging.create_collaboration_request(
                target_agent=target_agent_id,
                task_description=task_description,
                context=context,
                data_requirements=data_requirements
            )
            
            # Send to target agent
            target_endpoint = target_agent["endpoint"]
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{target_endpoint}/api/v1/collaborate",
                    json=secure_message,
                    headers={
                        "Content-Type": "application/json",
                        "X-Agent-ID": self.agent_id
                    },
                    timeout=aiohttp.ClientTimeout(total=context.get("timeout", 60))
                ) as response:
                    if response.status == 200:
                        response_data = await response.json()
                        
                        # Verify response signature
                        verified, message = self.secure_messaging.verify_secure_message(response_data)
                        
                        if verified:
                            return message["payload"]
                        else:
                            return {"error": "Invalid response signature"}
                    else:
                        error_text = await response.text()
                        return {"error": f"Collaboration failed: {response.status} - {error_text}"}
                        
        except asyncio.TimeoutError:
            return {"error": "Collaboration request timed out"}
        except Exception as e:
            logger.error(f"Collaboration request failed: {e}")
            return {"error": str(e)}
    
    def register_collaboration_handler(self, 
                                     message_type: str,
                                     handler: Callable[[Dict], Dict]):
        """Register a handler for collaboration requests."""
        self.collaboration_handlers[message_type] = handler
        logger.info(f"Registered handler for message type: {message_type}")
    
    async def handle_collaboration_request(self, secure_message: Dict) -> Dict:
        """Handle incoming collaboration request."""
        try:
            # Verify message
            verified, message = self.secure_messaging.verify_secure_message(secure_message)
            
            if not verified:
                return self._create_error_response("Invalid message signature")
            
            # Extract message details
            message_type = message.get("message_type")
            payload = message.get("payload", {})
            sender_id = message.get("sender_id")
            
            # Find appropriate handler
            handler = self.collaboration_handlers.get(message_type)
            
            if not handler:
                return self._create_error_response(f"No handler for message type: {message_type}")
            
            # Process request
            start_time = datetime.utcnow()
            
            try:
                result = await handler(payload) if asyncio.iscoroutinefunction(handler) else handler(payload)
                
                processing_time_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
                
                # Add metadata to result
                result["processing_time_ms"] = processing_time_ms
                result["agent_id"] = self.agent_id
                result["requester_id"] = sender_id
                
                # Create secure response
                return self.secure_messaging.create_collaboration_response(
                    request_id=message.get("nonce", "unknown"),
                    result=result,
                    status="completed"
                )
                
            except Exception as e:
                logger.error(f"Handler error: {e}")
                return self._create_error_response(f"Handler error: {str(e)}")
                
        except Exception as e:
            logger.error(f"Failed to handle collaboration request: {e}")
            return self._create_error_response(str(e))
    
    def _create_error_response(self, error_message: str) -> Dict:
        """Create an error response."""
        return self.secure_messaging.create_secure_message(
            recipient_id="requester",
            message_type="error",
            payload={"error": error_message}
        )
    
    def _get_agent_port(self) -> int:
        """Get the API port for this agent type."""
        port_map = {
            "hub": 8080,
            "finance": 8081,
            "marketing": 8082,
            "sales": 8083,
            "ceo": 8084
        }
        return port_map.get(self.agent_type, 8080)
    
    def _get_attestation_port(self) -> int:
        """Get the attestation port for this agent type."""
        port_map = {
            "hub": 29343,
            "finance": 29344,
            "marketing": 29345,
            "sales": 29346,
            "ceo": 29347
        }
        return port_map.get(self.agent_type, 29343)
    
    async def heartbeat_to_hub(self):
        """Send periodic heartbeat to hub."""
        if not self.hub_endpoint:
            return
        
        try:
            heartbeat_data = {
                "agent_id": self.agent_id,
                "status": "healthy",
                "timestamp": datetime.utcnow().isoformat()
            }
            
            async with aiohttp.ClientSession() as session:
                await session.post(
                    f"{self.hub_endpoint}/api/v1/agents/heartbeat",
                    json=heartbeat_data,
                    headers={"X-Agent-ID": self.agent_id},
                    timeout=aiohttp.ClientTimeout(total=5)
                )
                
        except Exception as e:
            logger.debug(f"Heartbeat failed: {e}")