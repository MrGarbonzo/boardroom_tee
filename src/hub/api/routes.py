"""Hub API routes."""

import logging
from fastapi import APIRouter, HTTPException, UploadFile, File, Depends, Header
from typing import Dict, List, Optional
import os

from ..models import AgentRegistration, OrchestrationRequest
from ..services import (
    UnifiedLLMManager,
    DocumentProcessor,
    AgentRegistry,
    OrchestrationEngine,
    VMCommunicationManager
)

logger = logging.getLogger(__name__)

router = APIRouter()

# Dependency injection placeholders (will be set by main.py)
_llm_manager = None
_document_processor = None
_agent_registry = None
_orchestration_engine = None
_vm_communication = None
_attestation_client = None


def set_services(llm_manager, document_processor, agent_registry, 
                orchestration_engine, vm_communication, attestation_client):
    """Set service dependencies."""
    global _llm_manager, _document_processor, _agent_registry
    global _orchestration_engine, _vm_communication, _attestation_client
    
    _llm_manager = llm_manager
    _document_processor = document_processor
    _agent_registry = agent_registry
    _orchestration_engine = orchestration_engine
    _vm_communication = vm_communication
    _attestation_client = attestation_client


def get_client_id(x_client_id: Optional[str] = Header(None)) -> str:
    """Extract client ID from headers."""
    if not x_client_id:
        raise HTTPException(status_code=400, detail="X-Client-ID header required")
    return x_client_id


# Document Management Endpoints

@router.post("/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    department: Optional[str] = None,
    tags: Optional[str] = None,
    client_id: str = Depends(get_client_id)
):
    """Upload and process a document."""
    try:
        # Read file content
        file_content = await file.read()
        
        # Prepare metadata
        metadata = {
            "department": department,
            "tags": tags.split(",") if tags else [],
            "original_filename": file.filename
        }
        
        # Process document
        result = await _document_processor.process_upload(
            file_content=file_content,
            filename=file.filename,
            metadata=metadata,
            client_id=client_id
        )
        
        if result["status"] == "failed":
            raise HTTPException(status_code=400, detail=result["error"])
        
        return {
            "status": "accepted",
            "upload_id": result["upload_id"],
            "document_id": result["document_id"],
            "processing_status": "completed",
            "categorization": result["categorization"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Document upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/documents/{document_id}")
async def get_document(
    document_id: str,
    client_id: str = Depends(get_client_id)
):
    """Get document by ID."""
    document = _document_processor.get_document(document_id)
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    if document["client_id"] != client_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return document


@router.get("/documents")
async def search_documents(
    department: Optional[str] = None,
    document_type: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    client_id: str = Depends(get_client_id)
):
    """Search documents with filters."""
    filters = {}
    if department:
        filters["department"] = department
    if document_type:
        filters["document_type"] = document_type
    if date_from:
        filters["date_from"] = date_from
    if date_to:
        filters["date_to"] = date_to
    
    documents = _document_processor.search_documents(client_id, filters)
    return {"documents": documents}


# Agent Management Endpoints

@router.post("/agents/register", status_code=201)
async def register_agent(
    registration: AgentRegistration,
    client_id: str = Depends(get_client_id),
    x_attestation_quote: Optional[str] = Header(None),
    x_public_key: Optional[str] = Header(None)
):
    """Register a new agent with attestation verification."""
    try:
        # Add headers to registration data if present
        if x_attestation_quote and x_public_key:
            registration.attestation_data["quote"] = x_attestation_quote
            registration.attestation_data["public_key"] = x_public_key
        
        result = await _agent_registry.register_agent(
            registration.dict(),
            client_id
        )
        
        if result["status"] == "rejected":
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Agent registration failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agents/directory")
async def get_agent_directory(
    capability: Optional[str] = None,
    client_id: str = Depends(get_client_id)
):
    """Get agent directory for client."""
    if capability:
        agents = _agent_registry.get_agents_by_capability(capability, client_id)
    else:
        agents = _agent_registry.get_agent_directory(client_id)
    
    return {"agents": agents}


@router.post("/agents/heartbeat")
async def agent_heartbeat(
    heartbeat_data: Dict,
    client_id: str = Depends(get_client_id)
):
    """Receive agent heartbeat."""
    agent_id = heartbeat_data.get("agent_id")
    if not agent_id:
        raise HTTPException(status_code=400, detail="agent_id required")
    
    success = _agent_registry.update_agent_heartbeat(agent_id, client_id)
    if not success:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    return {"status": "acknowledged"}


@router.get("/agents/health")
async def get_agents_health(client_id: str = Depends(get_client_id)):
    """Get health status of all agents."""
    health = _agent_registry.check_agent_health(client_id)
    vm_health = await _vm_communication.health_check_all_agents()
    
    return {
        "agent_registry": health,
        "vm_communication": vm_health
    }


# Orchestration Endpoints

@router.post("/orchestration/route")
async def route_collaboration_request(
    request: OrchestrationRequest,
    client_id: str = Depends(get_client_id)
):
    """Route collaboration request to appropriate agent."""
    try:
        result = await _orchestration_engine.route_request(
            request.dict(),
            client_id
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Orchestration routing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/orchestration/active")
async def get_active_requests(client_id: str = Depends(get_client_id)):
    """Get active orchestration requests."""
    active_requests = _orchestration_engine.get_active_requests(client_id)
    return {"active_requests": active_requests}


@router.post("/orchestration/response/{routing_id}")
async def process_collaboration_response(
    routing_id: str,
    response_data: Dict,
    client_id: str = Depends(get_client_id)
):
    """Process response from collaborating agent."""
    try:
        result = await _orchestration_engine.process_collaboration_response(
            routing_id,
            response_data
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Response processing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# System Health Endpoints

@router.get("/health")
async def health_check():
    """System health check."""
    try:
        llm_status = _llm_manager.is_loaded if _llm_manager else False
        memory_usage = _llm_manager.get_memory_usage() if _llm_manager else {}
        
        return {
            "status": "healthy",
            "timestamp": "2024-01-01T00:00:00Z",
            "services": {
                "llm_manager": {
                    "loaded": llm_status,
                    "memory": memory_usage
                },
                "document_processor": "healthy",
                "agent_registry": "healthy",
                "orchestration_engine": "healthy"
            },
            "development_mode": os.getenv('DEVELOPMENT_MODE', 'false').lower() == 'true'
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": "2024-01-01T00:00:00Z"
        }


@router.get("/attestation")
async def get_attestation_data():
    """Get hub attestation data for verification."""
    try:
        attestation_data = _attestation_client.get_attestation_endpoint_data()
        return attestation_data
        
    except Exception as e:
        logger.error(f"Attestation endpoint failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }