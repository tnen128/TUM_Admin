from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Dict, List, Optional
from enum import Enum
from app.api.models.document import (
    DocumentRequest, RefinementRequest, DocumentResponse,
    ExportRequest, DocumentType, ToneType
)
from app.api.services.export_service import DocumentExporter
import os
from datetime import datetime

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

class RefinementRequest(BaseModel):
    refinement_prompt: str

class DocumentResponse(BaseModel):
    document: str
    metadata: Dict[str, str]
    history: Optional[List[Dict[str, str]]] = None

# Initialize FastAPI
app = FastAPI(title="TUM Admin Assistant")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
document_exporter = DocumentExporter()

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
@app.post("/api/documents/generate", response_model=DocumentResponse)
async def generate_document(request: DocumentRequest):
    """Generate a new document"""
    try:
        response = get_test_response(request.doc_type.value, request.tone.value)
        return {
            "document": response,
            "metadata": {
                "doc_type": request.doc_type.value,
                "tone": request.tone.value,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            },
            "history": [{"user": request.prompt, "assistant": response}]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/documents/refine", response_model=DocumentResponse)
async def refine_document(request: RefinementRequest):
    """Refine an existing document"""
    try:
        response = f"""[Refined version based on: "{request.refinement_prompt}"]

This is a test refinement response.
The actual Gemini-powered refinement will be implemented later.

Best regards,
TUM Administration"""
        
        return {
            "document": response,
            "metadata": {
                "type": "refinement",
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            },
            "history": [{"user": request.refinement_prompt, "assistant": response}]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/documents/export")
async def export_document(request: ExportRequest):
    """Export document in the specified format"""
    try:
        # Generate the file
        filepath = document_exporter.export_document(
            request.document_content,
            request.metadata,
            request.format.value
        )
        
        # Get the filename from the filepath
        filename = os.path.basename(filepath)
        
        # Set the appropriate media type
        media_types = {
            "pdf": "application/pdf",
            "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "txt": "text/plain"
        }
        media_type = media_types.get(request.format.value, "application/octet-stream")
        
        # Return the file with proper headers
        return FileResponse(
            path=filepath,
            filename=filename,
            media_type=media_type,
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy"} 