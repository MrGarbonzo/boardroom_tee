"""VM Communication Manager for cross-VM agent communication."""

import os
import logging
import aiohttp
import asyncio
from typing import Dict, Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)


class VMCommunicationManager:
    """Manage communication with spoke VMs via IP addresses."""
    
    def __init__(self):
        self.spoke_endpoints = {}
        self.development_mode = os.getenv('DEVELOPMENT_MODE', 'false').lower() == 'true'
        self.load_spoke_endpoints_from_env()
    
    def load_spoke_endpoints_from_env(self):
        """Load spoke VM endpoints from environment variables."""
        # Load from .env file configured during deployment
        finance_endpoint = os.getenv('FINANCE_ENDPOINT')
        marketing_endpoint = os.getenv('MARKETING_ENDPOINT')
        sales_endpoint = os.getenv('SALES_ENDPOINT')
        
        if finance_endpoint:
            self.spoke_endpoints['finance'] = finance_endpoint
        if marketing_endpoint:
            self.spoke_endpoints['marketing'] = marketing_endpoint
        if sales_endpoint:
            self.spoke_endpoints['sales'] = sales_endpoint
        
        # Development mode defaults
        if self.development_mode:
            if 'finance' not in self.spoke_endpoints:
                self.spoke_endpoints['finance'] = 'http://localhost:8081'
            if 'marketing' not in self.spoke_endpoints:
                self.spoke_endpoints['marketing'] = 'http://localhost:8082'
        
        logger.info(f"Loaded spoke endpoints: {list(self.spoke_endpoints.keys())}")
    
    async def send_to_agent(self, agent_type: str, data: Dict) -> Dict:
        """Send data to specific agent VM via HTTP request."""
        if agent_type not in self.spoke_endpoints:
            return {"error": f"Agent VM {agent_type} not configured"}
        
        endpoint = self.spoke_endpoints[agent_type]
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{endpoint}/api/v1/process",
                    json=data,
                    headers={
                        "Content-Type": "application/json",
                        "X-Hub-Request": "true",
                        "X-Client-ID": os.getenv('CLIENT_ID', 'unknown')
                    },
                    timeout=aiohttp.ClientTimeout(total=data.get('timeout', 60))
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        logger.info(f"Successfully communicated with {agent_type} VM")
                        return result
                    else:
                        error_text = await response.text()
                        logger.error(f"Agent VM {agent_type} returned {response.status}: {error_text}")
                        return {
                            "error": f"Agent VM returned {response.status}",
                            "details": error_text
                        }
                        
        except asyncio.TimeoutError:
            logger.error(f"Timeout communicating with {agent_type} VM")
            return {"error": f"Timeout communicating with {agent_type} VM"}
        except Exception as e:
            logger.error(f"Failed to communicate with {agent_type} VM: {e}")
            return {"error": f"Communication failed: {str(e)}"}
    
    async def send_collaboration_request(self,
                                       agent_type: str,
                                       task_description: str,
                                       context: Dict,
                                       data_package: Dict) -> Dict:
        """Send collaboration request to agent VM."""
        data = {
            "type": "collaboration_request",
            "task_description": task_description,
            "context": context,
            "data_package": data_package,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return await self.send_to_agent(agent_type, data)
    
    async def health_check_all_agents(self) -> Dict:
        """Check health of all configured agent VMs."""
        health_results = {}
        
        for agent_type, endpoint in self.spoke_endpoints.items():
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        f"{endpoint}/health",
                        timeout=aiohttp.ClientTimeout(total=10)
                    ) as response:
                        if response.status == 200:
                            health_data = await response.json()
                            health_results[agent_type] = {
                                "status": "healthy",
                                "endpoint": endpoint,
                                "details": health_data,
                                "response_time_ms": response.headers.get('X-Response-Time', 'unknown')
                            }
                        else:
                            health_results[agent_type] = {
                                "status": "unhealthy",
                                "endpoint": endpoint,
                                "error": f"HTTP {response.status}"
                            }
            except Exception as e:
                health_results[agent_type] = {
                    "status": "unreachable",
                    "endpoint": endpoint,
                    "error": str(e)
                }
        
        return health_results
    
    async def check_agent_attestation(self, agent_type: str) -> Dict:
        """Check agent's attestation endpoint."""
        if agent_type not in self.spoke_endpoints:
            return {"error": f"Agent {agent_type} not configured"}
        
        # Calculate attestation port (API port + attestation offset)
        endpoint = self.spoke_endpoints[agent_type]
        base_url = endpoint.replace(':8081', ':29344').replace(':8082', ':29345')
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{base_url}/attestation",
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        attestation_data = await response.json()
                        return {
                            "status": "verified",
                            "attestation": attestation_data
                        }
                    else:
                        return {
                            "status": "unverified",
                            "error": f"Attestation endpoint returned {response.status}"
                        }
                        
        except Exception as e:
            return {
                "status": "unreachable",
                "error": str(e)
            }
    
    def get_configured_agents(self) -> List[str]:
        """Get list of configured agent types."""
        return list(self.spoke_endpoints.keys())
    
    def is_agent_configured(self, agent_type: str) -> bool:
        """Check if agent type is configured."""
        return agent_type in self.spoke_endpoints
    
    async def broadcast_to_all_agents(self, data: Dict) -> Dict:
        """Broadcast data to all configured agents."""
        results = {}
        
        # Send to all agents concurrently
        tasks = []
        for agent_type in self.spoke_endpoints.keys():
            task = self.send_to_agent(agent_type, data)
            tasks.append((agent_type, task))
        
        # Wait for all responses
        for agent_type, task in tasks:
            try:
                result = await task
                results[agent_type] = result
            except Exception as e:
                results[agent_type] = {"error": str(e)}
        
        return results