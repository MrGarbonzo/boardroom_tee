# API Specifications - Boardroom TEE

## Overview
Complete API documentation for hub endpoints, agent communication protocols, and frontend integration with attestation-verified messaging.

---

## Base Configuration
```
Base URL: https://hub-domain:8080
Authentication: Bearer token + Client ID
Content-Type: application/json
Attestation: Required for all data operations
```

## Hub API Endpoints

### Document Management

#### Upload Document
```http
POST /api/v1/documents/upload
Content-Type: multipart/form-data
Authorization: Bearer {token}
X-Client-ID: {client-id}
```

**Request:**
```json
{
  "file": "<binary_file_data>",
  "filename": "Q3_budget.xlsx",
  "metadata": {
    "department": "finance",
    "tags": ["budget", "quarterly"]
  }
}
```

**Response (202 Accepted):**
```json
{
  "status": "accepted",
  "upload_id": "doc_abc123def456",
  "processing_status": "queued",
  "estimated_completion": "2025-01-16T14:30:00Z"
}
```

#### Get Processing Status
```http
GET /api/v1/documents/{upload_id}/status
```

**Response:**
```json
{
  "upload_id": "doc_abc123def456",
  "status": "processing|completed|failed",
  "progress_percentage": 75,
  "result": {
    "document_id": "doc_789xyz",
    "categorization": {
      "department": "Finance",
      "document_type": "Data/Spreadsheet",
      "key_terms": ["budget", "quarterly", "revenue"],
      "confidence_score": 0.92
    }
  }
}
```

### Agent Management

#### Register Agent
```http
POST /api/v1/agents/register
X-Attestation-Quote: {base64_encoded_quote}
X-Public-Key: {agent_public_key}
```

**Request:**
```json
{
  "agent_id": "finance-agent-client123",
  "agent_type": "finance",
  "capabilities": ["financial_analysis", "roi_calculation", "budget_planning"],
  "endpoint": "https://finance-agent:8081",
  "attestation_data": {
    "quote": "base64_encoded_attestation_quote",
    "public_key": "agent_public_key_pem"
  }
}
```

**Response (201 Created):**
```json
{
  "status": "registered",
  "verification_status": "verified",
  "agent_id": "finance-agent-client123",
  "hub_public_key": "hub_public_key_for_agent_verification"
}
```

#### Route Collaboration Request
```http
POST /api/v1/orchestration/route
Authorization: Bearer {token}
X-Requesting-Agent: {agent_id}
X-Attestation-Signature: {request_signature}
```

**Request:**
```json
{
  "query": "I need marketing ROI analysis for Q4 holiday campaign",
  "requesting_agent": "finance-agent-client123",
  "context": {
    "budget_constraints": "$500K maximum",
    "timeframe": "Q4 2024"
  }
}
```

**Response:**
```json
{
  "routing_id": "route_456def789",
  "target_agent": "marketing-agent-client123",
  "estimated_time_minutes": 8,
  "data_package": {
    "encrypted_data_package": "base64_encrypted_data",
    "encryption_method": "agent_public_key"
  },
  "reasoning": "Marketing agent best positioned for ROI analysis"
}
```

---

## Agent-to-Agent Communication

### Collaboration Request
```http
POST /api/v1/collaborate
Host: {target-agent-endpoint}
X-Requesting-Agent: {requesting_agent_id}
X-Attestation-Quote: {requesting_agent_attestation}
X-Attestation-Signature: {message_signature}
```

**Request:**
```json
{
  "collaboration_id": "collab_123abc456",
  "task": {
    "type": "roi_analysis",
    "description": "Analyze ROI for Q4 holiday marketing campaign",
    "parameters": {
      "campaign_id": "holiday_2024_q4",
      "budget_limit": "$500K"
    }
  },
  "encrypted_data": {
    "package": "base64_encrypted_data_for_target_agent",
    "encryption_method": "target_agent_public_key"
  }
}
```

**Response:**
```json
{
  "collaboration_id": "collab_123abc456",
  "status": "completed",
  "analysis_result": {
    "roi_metrics": {
      "total_spend": "$485K",
      "revenue_generated": "$1.2M",
      "roi_percentage": "147%"
    },
    "recommendations": [
      "Increase email marketing budget for Q1",
      "Optimize search ad targeting"
    ]
  },
  "confidence_score": 0.91,
  "attestation_verification": {
    "requesting_agent_verified": true,
    "verification_timestamp": "2025-01-16T16:10:00Z"
  }
}
```

---

## Frontend Integration

### Authentication
```http
POST /api/v1/auth/login
```

**Request:**
```json
{
  "email": "cfo@company.com",
  "password": "secure_password",
  "client_id": "client123",
  "mfa_token": "123456"
}
```

**Response:**
```json
{
  "access_token": "jwt_access_token",
  "refresh_token": "jwt_refresh_token",
  "expires_in": 3600,
  "user_info": {
    "name": "John Smith",
    "role": "cfo",
    "permissions": ["view_financial_data", "access_all_agents"]
  }
}
```

### Dashboard Overview
```http
GET /api/v1/dashboard/overview
Authorization: Bearer {token}
```

**Response:**
```json
{
  "agent_status": {
    "available_agents": [
      {
        "agent_type": "finance",
        "status": "online",
        "attestation_verified": true
      }
    ]
  },
  "recent_activity": [
    {
      "timestamp": "2025-01-16T15:45:00Z",
      "activity": "Marketing ROI analysis completed",
      "agents_involved": ["finance", "marketing"]
    }
  ]
}
```

### Chat with Agent
```http
POST /api/v1/chat/agent/{agent_type}
Authorization: Bearer {token}
```

**Request:**
```json
{
  "message": "What was our customer acquisition cost for Q4?",
  "conversation_id": "conv_123abc",
  "collaboration_preferences": {
    "allow_cross_agent_collaboration": true
  }
}
```

**Response:**
```json
{
  "response_id": "resp_789def",
  "responding_agent": "marketing",
  "message": "Based on Q4 campaign data, our customer acquisition cost was $85 per customer, down 12% from Q3.",
  "collaboration_summary": {
    "agents_consulted": ["marketing", "finance"],
    "processing_time_seconds": 8
  },
  "confidence_score": 0.94
}
```

---

## Error Handling

### Standard HTTP Status Codes
- **200 OK**: Request successful
- **201 Created**: Resource created
- **400 Bad Request**: Invalid request format
- **401 Unauthorized**: Authentication required
- **403 Forbidden**: Insufficient permissions
- **500 Internal Server Error**: Server error

### Custom Error Response Format
```json
{
  "error": {
    "code": "ATTESTATION_VERIFICATION_FAILED",
    "message": "Agent attestation verification failed",
    "details": "The requesting agent's attestation quote could not be verified",
    "timestamp": "2025-01-16T16:30:00Z",
    "request_id": "req_123abc456"
  },
  "context": {
    "agent_id": "finance-agent-client123",
    "expected_mrtd": "ba87a347...",
    "received_mrtd": "different_hash..."
  }
}
```

### Domain-Specific Errors

#### Attestation Errors
- **ATTESTATION_VERIFICATION_FAILED**: Agent attestation verification failed
- **ATTESTATION_EXPIRED**: Agent attestation has expired
- **AGENT_NOT_VERIFIED**: Target agent not in verified registry

#### Agent Communication Errors
- **AGENT_OFFLINE**: Target agent not responding
- **COLLABORATION_TIMEOUT**: Agent collaboration request timed out
- **ENCRYPTION_FAILED**: Message encryption/decryption failed

#### Document Processing Errors
- **DOCUMENT_TOO_LARGE**: File exceeds maximum size limit
- **PROCESSING_QUEUE_FULL**: Processing queue at capacity
- **CATEGORIZATION_FAILED**: LLM categorization failed

---

## Security Headers

### Required Headers
```http
Strict-Transport-Security: max-age=31536000; includeSubDomains
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
```

### Attestation Headers
```http
X-Attestation-Quote: {base64_encoded_attestation}
X-Attestation-Signature: {request_signature}
X-Public-Key: {sender_public_key}
X-Timestamp: {unix_timestamp}
X-Nonce: {unique_request_nonce}
```

---

## Rate Limiting

### Limits by Endpoint Type
- **Document Upload**: 10 requests/minute per client
- **Agent Operations**: 30 requests/minute per agent
- **Dashboard Data**: 60 requests/minute per user

### Rate Limit Headers
```http
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1642345200
```

---

*Last Updated: December 2024*  
*Related: [`05-security/attestation-implementation.md`](../05-security/attestation-implementation.md) for security details*  
*Purpose: Complete API reference for Claude implementation*