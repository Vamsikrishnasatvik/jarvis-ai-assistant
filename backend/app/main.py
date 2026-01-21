from fastapi import FastAPI, UploadFile, File, HTTPException, status
from app.vector_store import vector_store
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime
import traceback

from .config import settings
from .models import (
    ChatRequest,
    ChatResponse,
    KnowledgeEntry,
    KnowledgeResponse,
    KnowledgeListResponse,
    DeleteResponse,
    HealthResponse
)
from .vector_store import vector_store
from .llm_service import llm_service

# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Personal AI Assistant with LLM and Vector Database"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint - health check"""
    return HealthResponse(
        status="running",
        version=settings.VERSION,
        timestamp=datetime.now()
    )

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        version=settings.VERSION,
        timestamp=datetime.now()
    )

@app.post(f"{settings.API_V1_STR}/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat endpoint with RAG (Retrieval-Augmented Generation)
    
    Takes user message, retrieves relevant context from vector store,
    and generates response using LLM
    """
    try:
        print(f"\n{'='*50}")
        print(f"Chat Request: {request.message[:100]}...")
        
        # Retrieve relevant context from vector store
        context_results = vector_store.search(
            request.message,
            top_k=settings.MAX_CONTEXT_LENGTH
        )
        
        # Extract text from results
        context = [result["text"] for result in context_results]
        
        print(f"Retrieved {len(context)} context sources")
        
        # Generate response using LLM
        response_text = await llm_service.generate_response(
            prompt=request.message,
            context=context,
            conversation_history=request.conversation_history
        )
        
        print(f"Generated response: {response_text[:100]}...")
        print(f"{'='*50}\n")
        
        return ChatResponse(
            response=response_text,
            sources=context,
            timestamp=datetime.now()
        )
        
    except Exception as e:
        print(f"Error in chat endpoint: {str(e)}")
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating response: {str(e)}"
        )

@app.post(f"{settings.API_V1_STR}/knowledge", response_model=KnowledgeResponse)
async def add_knowledge(entry: KnowledgeEntry):
    """
    Add knowledge entry to vector store
    
    Accepts text and optional metadata, generates embeddings,
    and stores in vector database
    """
    try:
        print(f"\nAdding knowledge: {entry.text[:100]}...")
        
        # Add to vector store
        entry_id = vector_store.add_knowledge(
            text=entry.text,
            metadata=entry.metadata
        )
        
        print(f"Knowledge added with ID: {entry_id}")
        
        return KnowledgeResponse(
            id=entry_id,
            text=entry.text,
            timestamp=datetime.now(),
            success=True
        )
        
    except Exception as e:
        print(f"Error adding knowledge: {str(e)}")
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error adding knowledge: {str(e)}"
        )

@app.get(f"{settings.API_V1_STR}/knowledge", response_model=KnowledgeListResponse)
async def list_knowledge():
    """
    List all knowledge entries
    
    Returns all entries in the vector store (without embeddings)
    """
    try:
        knowledge_list = vector_store.list_all()
        
        return KnowledgeListResponse(
            knowledge=knowledge_list,
            count=len(knowledge_list)
        )
        
    except Exception as e:
        print(f"Error listing knowledge: {str(e)}")
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving knowledge: {str(e)}"
        )

@app.delete(f"{settings.API_V1_STR}/knowledge/{{entry_id}}", response_model=DeleteResponse)
async def delete_knowledge(entry_id: str):
    """
    Delete a knowledge entry by ID
    """
    try:
        print(f"\nDeleting knowledge entry: {entry_id}")
        
        success = vector_store.delete(entry_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Knowledge entry not found: {entry_id}"
            )
        
        return DeleteResponse(
            success=True,
            id=entry_id,
            message="Knowledge entry deleted successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error deleting knowledge: {str(e)}")
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting knowledge: {str(e)}"
        )

@app.post(f"{settings.API_V1_STR}/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Upload and process document
    
    Accepts text files, extracts content, and adds to knowledge base
    """
    try:
        print(f"\nUploading file: {file.filename}")
        
        # Read file content
        content = await file.read()
        
        # Decode content (assuming text file)
        try:
            text = content.decode('utf-8')
        except UnicodeDecodeError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File must be a text file (UTF-8 encoded)"
            )
        
        # Add to vector store with file metadata
        entry_id = vector_store.add_knowledge(
            text=text,
            metadata={
                "filename": file.filename,
                "content_type": file.content_type,
                "size": len(content)
            }
        )
        
        print(f"File processed and added with ID: {entry_id}")
        
        return {
            "success": True,
            "id": entry_id,
            "filename": file.filename,
            "size": len(content),
            "message": "File processed and added to knowledge base successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error processing file: {str(e)}")
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing file: {str(e)}"
        )

@app.get(f"{settings.API_V1_STR}/stats")
async def get_stats():
    """Get statistics about the vector store"""
    try:
        stats = vector_store.get_stats()
        return {
            "vector_store": stats,
            "llm_model": settings.LLM_MODEL_NAME,
            "embedding_model": settings.EMBEDDING_MODEL,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        print(f"Error getting stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving statistics: {str(e)}"
        )

# Error handlers
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    print(f"Unhandled exception: {str(exc)}")
    traceback.print_exc()
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An unexpected error occurred"}
    )
@app.get("/vector-stats", tags=["Debug"])
def vector_stats():
    return vector_store.get_stats()

if __name__ == "__main__":
    import uvicorn # type: ignore
    print(f"\n{'='*60}")
    print(f"Starting {settings.PROJECT_NAME}")
    print(f"Version: {settings.VERSION}")
    print(f"{'='*60}\n")
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
        
    )