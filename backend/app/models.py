from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class ChatMessage(BaseModel):
    """Single chat message"""
    role: str = Field(..., description="Role: 'user' or 'assistant'")
    content: str = Field(..., description="Message content")
    timestamp: Optional[datetime] = Field(default_factory=datetime.now)

class ChatRequest(BaseModel):
    """Request for chat endpoint"""
    message: str = Field(..., description="User message", min_length=1)
    conversation_history: Optional[List[ChatMessage]] = Field(
        default=[],
        description="Previous conversation messages"
    )

class ChatResponse(BaseModel):
    """Response from chat endpoint"""
    response: str = Field(..., description="Assistant response")
    sources: List[str] = Field(
        default=[],
        description="Knowledge sources used for context"
    )
    timestamp: datetime = Field(default_factory=datetime.now)

class KnowledgeEntry(BaseModel):
    """Request to add knowledge"""
    text: str = Field(..., description="Knowledge text to add", min_length=1)
    metadata: Optional[Dict[str, Any]] = Field(
        default={},
        description="Additional metadata"
    )

class KnowledgeResponse(BaseModel):
    """Response from adding knowledge"""
    id: str = Field(..., description="Unique knowledge entry ID")
    text: str = Field(..., description="The knowledge text")
    timestamp: datetime = Field(default_factory=datetime.now)
    success: bool = Field(default=True, description="Success status")

class KnowledgeListResponse(BaseModel):
    """List of all knowledge entries"""
    knowledge: List[Dict[str, Any]] = Field(
        default=[],
        description="List of knowledge entries"
    )
    count: int = Field(default=0, description="Total number of entries")

class DeleteResponse(BaseModel):
    """Response from delete operation"""
    success: bool = Field(..., description="Success status")
    id: str = Field(..., description="Deleted entry ID")
    message: str = Field(default="Entry deleted successfully")

class HealthResponse(BaseModel):
    """Health check response"""
    status: str = Field(default="healthy")
    version: str = Field(...)
    timestamp: datetime = Field(default_factory=datetime.now)