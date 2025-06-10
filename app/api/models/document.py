from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from enum import Enum

class DocumentType(str, Enum):
    ANNOUNCEMENT = "Announcement"
    STUDENT_COMMUNICATION = "Student Communication"
    MEETING_SUMMARY = "Meeting Summary"

class ToneType(str, Enum):
    NEUTRAL = "Neutral"
    FRIENDLY = "Friendly"
    FIRM = "Firm but polite"
    FORMAL = "Formal"

class ExportFormat(str, Enum):
    PDF = "pdf"
    DOCX = "docx"
    TXT = "txt"

class DocumentRequest(BaseModel):
    prompt: str = Field(..., min_length=10, description="The document generation prompt")
    doc_type: DocumentType
    tone: ToneType

class RefinementRequest(BaseModel):
    refinement_prompt: str = Field(..., min_length=10, description="The refinement instructions")

class ExportRequest(BaseModel):
    format: ExportFormat = Field(..., description="The desired export format")
    document_content: str = Field(..., description="The document content to export")
    metadata: Dict[str, str] = Field(..., description="Document metadata")

class DocumentResponse(BaseModel):
    document: str
    metadata: Dict[str, str]
    history: Optional[List[Dict[str, str]]] = None 