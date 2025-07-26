"""Finance Agent - Main application entry point."""

import asyncio
import logging
import os
import sys
from contextlib import asynccontextmanager

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from fastapi import FastAPI
import uvicorn

from agents.finance.finance_agent import FinanceAgent
from agents.finance.api.routes import router as finance_router, set_services

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global services
finance_agent = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting Finance Agent...")
    
    try:
        global finance_agent
        
        # Initialize finance agent
        client_id = os.getenv('CLIENT_ID', 'default')
        finance_agent = FinanceAgent(client_id=client_id)
        
        # Initialize agent
        await finance_agent.initialize()
        
        # Set services for API routes
        set_services(finance_agent, finance_agent.financial_analyzer)
        
        # Start heartbeat loop
        asyncio.create_task(finance_agent.start_heartbeat_loop())
        
        logger.info("Finance Agent initialized successfully")
        logger.info(f"Agent ID: {finance_agent.agent_id}")
        logger.info(f"Hub endpoint: {finance_agent.hub_endpoint}")
        logger.info(f"Development mode: {finance_agent.development_mode}")
        
        yield
        
    except Exception as e:
        logger.error(f"Failed to initialize Finance Agent: {e}")
        raise
    
    # Shutdown
    logger.info("Shutting down Finance Agent...")
    
    if finance_agent:
        await finance_agent.shutdown()


# Create FastAPI application
app = FastAPI(
    title="Boardroom TEE Finance Agent",
    description="Specialized financial analysis agent with AdaptLLM/finance-LLM",
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
app.include_router(finance_router, prefix="/api/v1")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "Boardroom TEE Finance Agent",
        "version": "1.0.0",
        "agent_type": "finance",
        "model": "AdaptLLM/finance-LLM",
        "status": "running",
        "development_mode": os.getenv('DEVELOPMENT_MODE', 'false').lower() == 'true'
    }


@app.get("/health")
async def health_check():
    """Basic health check endpoint."""
    try:
        if not finance_agent:
            return {
                "status": "unhealthy",
                "error": "Agent not initialized",
                "service": "finance-agent"
            }
        
        # Get comprehensive health info
        health_info = await finance_agent.handle_health_check({})
        
        # Add service-specific info
        health_info.update({
            "service": "finance-agent",
            "model_loaded": finance_agent.finance_llm.is_loaded,
            "hub_registered": finance_agent.is_running,
            "port": int(os.getenv("AGENT_API_PORT", "8081"))
        })
        
        return health_info
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "service": "finance-agent"
        }


# Attestation endpoint (port 29344)
@app.get("/attestation")
async def attestation_endpoint():
    """TEE attestation verification endpoint."""
    try:
        if not finance_agent:
            return {"status": "unhealthy", "error": "Agent not initialized"}
        
        return finance_agent.attestation_client.get_attestation_endpoint_data()
        
    except Exception as e:
        logger.error(f"Attestation endpoint error: {e}")
        return {"status": "unhealthy", "error": str(e)}


if __name__ == "__main__":
    # Get configuration from environment
    host = os.getenv("AGENT_HOST", "0.0.0.0")
    port = int(os.getenv("AGENT_API_PORT", "8081"))
    log_level = os.getenv("LOG_LEVEL", "info").lower()
    
    # Run the application
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        log_level=log_level,
        reload=os.getenv('DEVELOPMENT_MODE', 'false').lower() == 'true'
    )