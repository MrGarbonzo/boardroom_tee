"""Boardroom TEE Hub - Main application entry point."""

import asyncio
import logging
import os
import sys
from contextlib import asynccontextmanager

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from fastapi import FastAPI
import uvicorn

# Shared services
from shared import TEEKeyManager, AttestationClient, SecureMessaging, AgentCommunication

# Hub services
from hub.services import (
    UnifiedLLMManager,
    DocumentProcessor,
    AgentRegistry,
    OrchestrationEngine,
    VMCommunicationManager
)

# API routes
from hub.api.routes import router as hub_router, set_services

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global services
services = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting Boardroom TEE Hub...")
    
    try:
        # Initialize TEE services
        key_manager = TEEKeyManager()
        attestation_client = AttestationClient()
        
        # Load or generate keys
        if not key_manager.load_keys():
            logger.info("Generating new TEE keys...")
            key_manager.generate_tee_keys()
        
        # Initialize secure messaging
        secure_messaging = SecureMessaging(key_manager)
        
        # Initialize hub services
        llm_manager = UnifiedLLMManager()
        await llm_manager.load_model()
        
        document_processor = DocumentProcessor(llm_manager)
        agent_registry = AgentRegistry(attestation_client)
        vm_communication = VMCommunicationManager()
        
        orchestration_engine = OrchestrationEngine(
            llm_manager,
            agent_registry,
            vm_communication
        )
        
        # Store services globally
        services.update({
            'key_manager': key_manager,
            'attestation_client': attestation_client,
            'secure_messaging': secure_messaging,
            'llm_manager': llm_manager,
            'document_processor': document_processor,
            'agent_registry': agent_registry,
            'orchestration_engine': orchestration_engine,
            'vm_communication': vm_communication
        })
        
        # Set services for API routes
        set_services(
            llm_manager,
            document_processor,
            agent_registry,
            orchestration_engine,
            vm_communication,
            attestation_client
        )
        
        logger.info("Hub services initialized successfully")
        logger.info(f"Hub running in {'development' if os.getenv('DEVELOPMENT_MODE') == 'true' else 'production'} mode")
        
        yield
        
    except Exception as e:
        logger.error(f"Failed to initialize hub services: {e}")
        raise
    
    # Shutdown
    logger.info("Shutting down Hub services...")
    
    # Cleanup
    if 'llm_manager' in services:
        # In production, would cleanup model memory
        pass


# Create FastAPI application
app = FastAPI(
    title="Boardroom TEE Hub",
    description="Central hub for document processing and agent orchestration",
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
app.include_router(hub_router, prefix="/api/v1")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "Boardroom TEE Hub",
        "version": "1.0.0",
        "status": "running",
        "development_mode": os.getenv('DEVELOPMENT_MODE', 'false').lower() == 'true'
    }


@app.get("/health")
async def health_check():
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "service": "hub",
        "model_loaded": services.get('llm_manager', {}).is_loaded if 'llm_manager' in services else False,
        "registered_agents": len(services.get('agent_registry', {}).agents) if 'agent_registry' in services else 0,
        "development_mode": os.getenv('DEVELOPMENT_MODE', 'false').lower() == 'true'
    }


# Attestation endpoint (port 29343)
@app.get("/attestation")
async def attestation_endpoint():
    """TEE attestation verification endpoint."""
    try:
        attestation_client = services.get('attestation_client')
        if not attestation_client:
            return {"status": "unhealthy", "error": "Attestation client not initialized"}
        
        return attestation_client.get_attestation_endpoint_data()
        
    except Exception as e:
        logger.error(f"Attestation endpoint error: {e}")
        return {"status": "unhealthy", "error": str(e)}


if __name__ == "__main__":
    # Get configuration from environment
    host = os.getenv("HUB_HOST", "0.0.0.0")
    port = int(os.getenv("HUB_API_PORT", "8080"))
    log_level = os.getenv("LOG_LEVEL", "info").lower()
    
    # Run the application
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        log_level=log_level,
        reload=os.getenv('DEVELOPMENT_MODE', 'false').lower() == 'true'
    )