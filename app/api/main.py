from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse
from pydantic import BaseModel
from typing import Dict, List, Optional
from enum import Enum
from app.api.models.document import (
    DocumentRequest, RefinementRequest, DocumentResponse,
    ExportRequest, DocumentType, ToneType
)
from app.api.services.export_service import DocumentExporter
from app.api.services.llm_service import LLMService
import os
from datetime import datetime
import logging
import json
import asyncio

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Models
class DocumentType(str, Enum):
    ANNOUNCEMENT = "Announcement"
    STUDENT_COMMUNICATION = "Student Communication"
    MEETING_SUMMARY = "Meeting Summary"

class ToneType(str, Enum):
    NEUTRAL = "Neutral"
    FRIENDLY = "Friendly"
    FIRM = "Firm but polite"
    FORMAL = "Formal"

class DocumentRequest(BaseModel):
    prompt: str
    doc_type: DocumentType
    tone: ToneType
    additional_context: Optional[str] = None
    sender_name: Optional[str] = None
    sender_profession: Optional[str] = None
    language: Optional[str] = None

class RefinementRequest(BaseModel):
    refinement_prompt: str
    current_document: str
    doc_type: DocumentType
    tone: ToneType

class DocumentResponse(BaseModel):
    document: str
    metadata: Dict[str, str]
    history: Optional[List[Dict[str, str]]] = None

# Initialize FastAPI
app = FastAPI(title="TUM Admin Assistant")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
try:
    llm_service = LLMService()
    document_exporter = DocumentExporter()
    logger.info("Successfully initialized services")
except Exception as e:
    logger.error(f"Error initializing services: {str(e)}")
    raise

# Test Data
def get_test_response(doc_type: str, tone: str) -> str:
    responses = {
        "Announcement": f"""Dear Students,

We would like to inform you about an important update regarding course registration. 
This message is written in a {tone.lower()} tone.

The registration deadline has been extended by one week to accommodate system maintenance.
Please ensure you complete your registration by the new deadline.

Key Points:
- Original Deadline: March 15, 2024
- New Deadline: March 22, 2024
- Reason: System Maintenance

If you have any questions, please contact the student services office.

Best regards,
TUM Administration""",
    }
    return responses.get(doc_type, "Test document content")

# Routes
@app.post("/api/documents/generate")
async def generate_document(request: DocumentRequest):
    """Generate a document based on the request parameters."""
    try:
        logger.info(f"Generating document of type {request.doc_type} with tone {request.tone}")
        result = llm_service.generate_document(
            request.doc_type,
            request.tone,
            request.prompt,
            request.additional_context,
            request.sender_name,
            request.sender_profession,
            request.language
        )
        return result
    except Exception as e:
        logger.error(f"Error generating document: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/documents/refine")
async def refine_document(request: RefinementRequest):
    """Refine a document based on the refinement request."""
    try:
        logger.info(f"Refining document of type {request.doc_type} with tone {request.tone}")
        
        async def generate():
            async for chunk in llm_service.refine_document(
                request.current_document,
                request.refinement_prompt,
                request.doc_type,
                request.tone
            ):
                yield f"data: {json.dumps(chunk)}\n\n"
        
        return StreamingResponse(
            generate(),
            media_type="text/event-stream"
        )
    except Exception as e:
        logger.error(f"Error refining document: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/documents/export")
async def export_document(request: ExportRequest):
    """Export a document in the specified format."""
    try:
        logger.info(f"Exporting document in {request.format} format")
        result = document_exporter.export_document(request.document_content, request.metadata, request.format)
        return FileResponse(result, filename=os.path.basename(result))
    except Exception as e:
        logger.error(f"Error exporting document: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"} 