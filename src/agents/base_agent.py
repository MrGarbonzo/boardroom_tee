"""Base agent class for all specialized agents."""

import os
import logging
import asyncio
import sys
from typing import Dict, List, Optional, Callable
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from shared import TEEKeyManager, AttestationClient, SecureMessaging, AgentCommunication

logger = logging.getLogger(__name__)


class BaseAgent:
    """Base class for all Boardroom TEE agents."""
    
    def __init__(self, agent_id: str, agent_type: str, capabilities: List[str]):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.capabilities = capabilities
        self.development_mode = os.getenv('DEVELOPMENT_MODE', 'false').lower() == 'true'
        self.is_running = False
        
        # Initialize TEE components
        self.key_manager = TEEKeyManager()
        self.attestation_client = AttestationClient()
        self.secure_messaging = SecureMessaging(self.key_manager)
        
        # Agent communication
        self.hub_endpoint = os.getenv('HUB_ENDPOINT', 'http://localhost:8080')
        self.communication = AgentCommunication(
            agent_id=agent_id,
            agent_type=agent_type,
            key_manager=self.key_manager,
            attestation_client=self.attestation_client,
            secure_messaging=self.secure_messaging
        )
        
        # Request handlers
        self.request_handlers = {}
        
    async def initialize(self):
        """Initialize the agent."""
        try:
            logger.info(f"Initializing {self.agent_type} agent: {self.agent_id}")
            
            # Load or generate TEE keys
            if not self.key_manager.load_keys():
                logger.info("Generating new TEE keys...")
                self.key_manager.generate_tee_keys()
            
            # Register default handlers
            self.register_handlers()
            
            # Register with hub
            if self.hub_endpoint:
                success = await self.communication.register_with_hub(
                    self.hub_endpoint,
                    self.capabilities
                )
                
                if success:
                    logger.info(f"Successfully registered with hub: {self.hub_endpoint}")
                else:
                    logger.warning("Failed to register with hub")
            
            self.is_running = True
            logger.info(f"Agent {self.agent_id} initialized successfully")
            
        except Exception as e:
            logger.error(f"Agent initialization failed: {e}")
            raise
    
    def register_handlers(self):
        """Register default request handlers. Override in subclasses."""
        # Register collaboration handler
        self.communication.register_collaboration_handler(
            "collaboration_request",
            self.handle_collaboration_request
        )
        
        # Register health check handler
        self.register_handler("health_check", self.handle_health_check)
    
    def register_handler(self, message_type: str, handler: Callable):
        """Register a request handler."""
        self.request_handlers[message_type] = handler
        logger.info(f"Registered handler for: {message_type}")
    
    async def handle_collaboration_request(self, payload: Dict) -> Dict:
        """Handle collaboration request from another agent."""
        try:
            task_description = payload.get("task_description", "")
            context = payload.get("context", {})
            data_package = payload.get("data_package", {})
            
            logger.info(f"Received collaboration request: {task_description}")
            
            # Process the request (override in subclasses)
            result = await self.process_collaboration_request(
                task_description, context, data_package
            )
            
            return {
                "status": "completed",
                "result": result,
                "agent_id": self.agent_id,
                "agent_type": self.agent_type,
                "processed_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Collaboration request failed: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "agent_id": self.agent_id,
                "agent_type": self.agent_type
            }
    
    async def process_collaboration_request(self, 
                                          task_description: str,
                                          context: Dict,
                                          data_package: Dict) -> Dict:
        """Process collaboration request. Override in subclasses."""
        return {
            "message": "Base agent cannot process requests",
            "task": task_description,
            "context": context
        }
    
    async def handle_health_check(self, payload: Dict) -> Dict:
        """Handle health check request."""
        return {
            "status": "healthy",
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "capabilities": self.capabilities,
            "uptime_seconds": self.get_uptime(),
            "memory_usage": self.get_memory_usage(),
            "development_mode": self.development_mode
        }
    
    async def send_heartbeat(self):
        """Send periodic heartbeat to hub."""
        if self.is_running:
            await self.communication.heartbeat_to_hub()
    
    async def start_heartbeat_loop(self):
        """Start heartbeat loop."""
        while self.is_running:
            try:
                await self.send_heartbeat()
                await asyncio.sleep(60)  # Every minute
            except Exception as e:
                logger.error(f"Heartbeat failed: {e}")
                await asyncio.sleep(60)
    
    async def collaborate_with_agent(self,
                                   target_agent_type: str,
                                   task_description: str,
                                   context: Dict,
                                   data_requirements: List[str]) -> Dict:
        """Request collaboration from another agent."""
        try:
            # Find target agent ID (simplified - in production would be more sophisticated)
            target_agent_id = f"{target_agent_type}-agent-{os.getenv('CLIENT_ID', 'default')}"
            
            result = await self.communication.send_collaboration_request(
                target_agent_id=target_agent_id,
                task_description=task_description,
                context=context,
                data_requirements=data_requirements
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Collaboration with {target_agent_type} failed: {e}")
            return {"error": str(e)}
    
    def get_uptime(self) -> float:
        """Get agent uptime in seconds."""
        # Simplified implementation
        return 3600.0  # Mock 1 hour uptime
    
    def get_memory_usage(self) -> Dict:
        """Get memory usage statistics."""
        # In production, would use actual memory monitoring
        return {
            "used_mb": 100,
            "total_mb": 1000,
            "percentage": 10.0
        }
    
    async def shutdown(self):
        """Shutdown the agent gracefully."""
        logger.info(f"Shutting down agent: {self.agent_id}")
        self.is_running = False
        
        # Cleanup resources
        # In production, would cleanup model memory, close connections, etc.
        
        logger.info("Agent shutdown complete")