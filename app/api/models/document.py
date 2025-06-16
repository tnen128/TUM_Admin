from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from enum import Enum

class DocumentType(str, Enum):
    """
    DocumentType represents the type of document being generated.

    Args:
        str (Enum): The string representation of the document type.
        Enum: The enum type for the document type.
    """
    ANNOUNCEMENT = "Announcement"
    STUDENT_COMMUNICATION = "Student Communication"
    MEETING_SUMMARY = "Meeting Summary"

class ToneType(str, Enum):
    """
    ToneType represents the tone of the document being generated.

    Args:
        str (Enum): The string representation of the tone type.
        Enum: The enum type for the tone type.
    """
    NEUTRAL = "Neutral"
    FRIENDLY = "Friendly"
    FIRM = "Firm but polite"
    FORMAL = "Formal"

class ExportFormat(str, Enum):
    """
    ExportFormat represents the format in which the document is to be exported.

    Args:
        str (Enum): The string representation of the export format.
        Enum: The enum type for the export format.
    """
    PDF = "pdf"
    DOCX = "docx"
    TXT = "txt"

class DocumentRequest(BaseModel):
    """
    DocumentRequest represents the request for generating a document.

    Args:
        prompt (str): The prompt for generating the document.
        doc_type (DocumentType): The type of document being generated.
        tone (ToneType): The tone of the document being generated.
    """
    prompt: str = Field(..., min_length=10, description="The document generation prompt")
    doc_type: DocumentType
    tone: ToneType

class RefinementRequest(BaseModel):
    """
    RefinementRequest represents the request for refining a document.

    Args:
        refinement_prompt (str): The instructions for refining the document.
    """
    refinement_prompt: str = Field(..., min_length=10, description="The refinement instructions")

class ExportRequest(BaseModel):
    """
    ExportRequest represents the request for exporting a document.

    Args:
        format (ExportFormat): The desired format for exporting the document.
        document_content (str): The content of the document to be exported.
        metadata (Dict[str, str]): The metadata associated with the document.
    """
    format: ExportFormat = Field(..., description="The desired export format")
    document_content: str = Field(..., description="The document content to export")
    metadata: Dict[str, str] = Field(..., description="Document metadata")

class DocumentResponse(BaseModel):
    """
    DocumentResponse represents the response from generating a document.

    Args:
        document (str): The generated document content.
        metadata (Dict[str, str]): The metadata associated with the document.
        history (Optional[List[Dict[str, str]]]): The history of refinements applied to the document.
    """
    document: str
    metadata: Dict[str, str]
    history: Optional[List[Dict[str, str]]] = None 