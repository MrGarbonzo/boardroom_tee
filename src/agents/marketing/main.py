"""Marketing Agent - Main application entry point."""

import asyncio
import logging
import os
import sys
from contextlib import asynccontextmanager

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from fastapi import FastAPI
import uvicorn

from agents.marketing.marketing_agent import MarketingAgent
from agents.marketing.api.routes import router as marketing_router, set_services

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global services
marketing_agent = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting Marketing Agent...")
    
    try:
        global marketing_agent
        
        # Initialize marketing agent
        client_id = os.getenv('CLIENT_ID', 'default')
        marketing_agent = MarketingAgent(client_id=client_id)
        
        # Initialize agent
        await marketing_agent.initialize()
        
        # Set services for API routes
        set_services(marketing_agent, marketing_agent.campaign_analyzer)
        
        # Start heartbeat loop
        asyncio.create_task(marketing_agent.start_heartbeat_loop())
        
        logger.info("Marketing Agent initialized successfully")
        logger.info(f"Agent ID: {marketing_agent.agent_id}")
        logger.info(f"Hub endpoint: {marketing_agent.hub_endpoint}")
        logger.info(f"Development mode: {marketing_agent.development_mode}")
        
        yield
        
    except Exception as e:
        logger.error(f"Failed to initialize Marketing Agent: {e}")
        raise
    
    # Shutdown
    logger.info("Shutting down Marketing Agent...")
    
    if marketing_agent:
        await marketing_agent.shutdown()


# Create FastAPI application
app = FastAPI(
    title="Boardroom TEE Marketing Agent",
    description="Specialized marketing intelligence agent with Mistral-7B-Instruct",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware for development
if os.getenv('DEVELOPMENT_MODE', 'false').lower() == 'true':
    from fastapi.middleware.cors import CORSMiddleware
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Include API routes
app.include_router(marketing_router, prefix="/api/v1")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "Boardroom TEE Marketing Agent",
        "version": "1.0.0",
        "agent_type": "marketing",
        "model": "mistralai/Mistral-7B-Instruct-v0.3",
        "status": "running",
        "development_mode": os.getenv('DEVELOPMENT_MODE', 'false').lower() == 'true'
    }


@app.get("/health")
async def health_check():
    """Basic health check endpoint."""
    try:
        if not marketing_agent:
            return {
                "status": "unhealthy",
                "error": "Agent not initialized",
                "service": "marketing-agent"
            }
        
        # Get comprehensive health info
        health_info = await marketing_agent.handle_health_check({})
        
        # Add service-specific info
        health_info.update({
            "service": "marketing-agent",
            "model_loaded": marketing_agent.marketing_llm.is_loaded,
            "hub_registered": marketing_agent.is_running,
            "port": int(os.getenv("AGENT_API_PORT", "8082"))
        })
        
        return health_info
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "service": "marketing-agent"
        }


# Attestation endpoint (port 29345)
@app.get("/attestation")
async def attestation_endpoint():
    """TEE attestation verification endpoint."""
    try:
        if not marketing_agent:
            return {"status": "unhealthy", "error": "Agent not initialized"}
        
        return marketing_agent.attestation_client.get_attestation_endpoint_data()
        
    except Exception as e:
        logger.error(f"Attestation endpoint error: {e}")
        return {"status": "unhealthy", "error": str(e)}


if __name__ == "__main__":
    # Get configuration from environment
    host = os.getenv("AGENT_HOST", "0.0.0.0")
    port = int(os.getenv("AGENT_API_PORT", "8082"))
    log_level = os.getenv("LOG_LEVEL", "info").lower()
    
    # Run the application
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        log_level=log_level,
        reload=os.getenv('DEVELOPMENT_MODE', 'false').lower() == 'true'
    )