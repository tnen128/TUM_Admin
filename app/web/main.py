import streamlit as st
import requests
from dotenv import load_dotenv
import os
import base64
from datetime import datetime
import json
from typing import Dict, Any
import time
import io
from enum import Enum

# Try to import from the API models, fallback to local definitions if it fails
try:
    from app.api.models.document import DocumentType, ToneType
except ImportError:
    # Fallback: Define the enums locally
    class DocumentType(str, Enum):
        ANNOUNCEMENT = "Announcement"
        STUDENT_COMMUNICATION = "Student Communication"
        MEETING_SUMMARY = "Meeting Summary"

    class ToneType(str, Enum):
        NEUTRAL = "Neutral"
        FRIENDLY = "Friendly"
        FIRM = "Firm but polite"
        FORMAL = "Formal"

# Load environment variables
load_dotenv()

# Configure the page
st.set_page_config(
    page_title="TUM Admin Assistant",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for TUM-branded chat interface
st.markdown("""
<style>
    /* TUM Colors */
    :root {
        --tum-blue: #0064AA;
        --tum-light-blue: #0077B6;
        --tum-dark-blue: #003359;
        --tum-gray: #E6E6E6;
        --tum-dark-gray: #333333;
        --tum-accent: #FF6B35;
        --tum-success: #28a745;
        --tum-warning: #ffc107;
        --tum-danger: #dc3545;
    }

    /* Main container styling */
    .main {
        padding: 0;
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        min-height: 100vh;
        display: flex;
        flex-direction: column;
        position: relative;
        overflow-x: hidden;
        overflow-y: auto;
    }

    .main::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grain" width="100" height="100" patternUnits="userSpaceOnUse"><circle cx="50" cy="50" r="1" fill="%230064AA" opacity="0.03"/></pattern></defs><rect width="100" height="100" fill="url(%23grain)"/></svg>');
        pointer-events: none;
        z-index: 0;
    }

    /* Ensure body allows scrolling */
    body {
        overflow-x: hidden;
        overflow-y: auto;
    }

    .stApp {
        max-width: 100%;
        padding: 0;
        min-height: 100vh;
        background: transparent;
        overflow-x: hidden;
        overflow-y: auto;
    }

    /* Header styling */
    .main h1 {
        color: var(--tum-blue);
        font-size: 2.5rem;
        font-weight: 700;
        text-align: center;
        margin: 2rem 0;
        padding: 1rem;
        border-radius: 1rem;
        box-shadow: 0 8px 32px rgba(0, 100, 170, 0.1);
        animation: slideInDown 0.8s ease-out;
        position: relative;
        z-index: 1;
    }

    .main h1::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(135deg, rgba(255,255,255,0.1), rgba(255,255,255,0.05));
        border-radius: 1rem;
        z-index: -1;
    }

    /* Chat container */
    .chat-container {
        flex: 1;
        overflow-y: auto;
        padding: 2rem;
        margin-bottom: 100px;
        display: flex;
        flex-direction: column;
        position: relative;
        z-index: 1;
        background: rgba(255, 255, 255, 0.8);
        backdrop-filter: blur(10px);
        border-radius: 1.5rem;
        margin: 1rem 2rem 120px 2rem;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        max-height: calc(100vh - 200px);
    }

    /* Custom scrollbar */
    .chat-container::-webkit-scrollbar {
        width: 8px;
    }

    .chat-container::-webkit-scrollbar-track {
        background: rgba(0, 100, 170, 0.1);
        border-radius: 4px;
    }

    .chat-container::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, var(--tum-blue), var(--tum-light-blue));
        border-radius: 4px;
        transition: all 0.3s ease;
    }

    .chat-container::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, var(--tum-light-blue), var(--tum-blue));
    }

    /* Chat messages */
    .chat-message {
        padding: 1.5rem;
        border-radius: 1.5rem;
        margin-bottom: 1.5rem;
        max-width: 85%;
        display: flex;
        flex-direction: column;
        animation: messageSlideIn 0.5s ease-out;
        position: relative;
        transition: all 0.3s ease;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
    }

    .chat-message:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.15);
    }

    .chat-message.user {
        background: linear-gradient(135deg, var(--tum-blue), var(--tum-light-blue));
        color: white;
        margin-left: auto;
        border-bottom-right-radius: 0.5rem;
        animation: messageSlideInRight 0.5s ease-out;
    }

    .chat-message.user::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(135deg, rgba(255,255,255,0.1), rgba(255,255,255,0.05));
        border-radius: 1.5rem;
        border-bottom-right-radius: 0.5rem;
        z-index: -1;
    }

    .chat-message.assistant {
        background: linear-gradient(135deg, #ffffff, #f8f9fa);
        color: var(--tum-dark-gray);
        margin-right: auto;
        border-bottom-left-radius: 0.5rem;
        border: 1px solid rgba(0, 100, 170, 0.1);
        animation: messageSlideInLeft 0.5s ease-out;
    }

    .chat-message.assistant::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(135deg, rgba(0, 100, 170, 0.02), rgba(0, 100, 170, 0.05));
        border-radius: 1.5rem;
        border-bottom-left-radius: 0.5rem;
        z-index: -1;
    }

    .chat-message .content {
        display: flex;
        align-items: flex-start;
        gap: 1rem;
    }

    .chat-message .avatar {
        width: 42px;
        height: 42px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.3rem;
        background: linear-gradient(135deg, #ffffff, #f8f9fa);
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        flex-shrink: 0;
        transition: all 0.3s ease;
        border: 2px solid rgba(255, 255, 255, 0.3);
    }

    .chat-message:hover .avatar {
        transform: scale(1.1);
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
    }

    .chat-message .message {
        flex: 1;
        white-space: pre-wrap;
        line-height: 1.7;
        font-size: 1.05rem;
        font-weight: 400;
    }

    /* Input container */
    .input-container {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        padding: 1.5rem 2rem;
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        border-top: 1px solid rgba(0, 100, 170, 0.1);
        display: flex;
        gap: 1rem;
        align-items: center;
        box-shadow: 0 -10px 30px rgba(0, 0, 0, 0.1);
        z-index: 10;
        animation: slideInUp 0.5s ease-out;
        pointer-events: auto;
    }

    .input-container textarea {
        flex: 1;
        background: rgba(255, 255, 255, 0.9);
        color: var(--tum-dark-gray);
        border: 2px solid rgba(0, 100, 170, 0.2);
        border-radius: 1.5rem;
        padding: 1rem 1.5rem;
        resize: none;
        height: 60px;
        transition: all 0.3s ease;
        font-size: 1.05rem;
        line-height: 1.5;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
    }

    .input-container textarea:focus {
        border-color: var(--tum-blue);
        box-shadow: 0 0 0 4px rgba(0, 100, 170, 0.1), 0 8px 25px rgba(0, 0, 0, 0.1);
        outline: none;
        transform: translateY(-2px);
    }

    .input-container button {
        background: linear-gradient(135deg, var(--tum-blue), var(--tum-light-blue));
        color: white;
        border: none;
        padding: 1rem 2rem;
        border-radius: 1.5rem;
        cursor: pointer;
        display: flex;
        align-items: center;
        gap: 0.75rem;
        transition: all 0.3s ease;
        font-weight: 600;
        font-size: 1.05rem;
        height: 60px;
        box-shadow: 0 6px 20px rgba(0, 100, 170, 0.3);
        position: relative;
        overflow: hidden;
    }

    .input-container button::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
        transition: left 0.5s ease;
    }

    .input-container button:hover::before {
        left: 100%;
    }

    .input-container button:hover {
        background: linear-gradient(135deg, var(--tum-light-blue), var(--tum-blue));
        transform: translateY(-3px);
        box-shadow: 0 10px 30px rgba(0, 100, 170, 0.4);
    }

    .input-container button:active {
        transform: translateY(-1px);
    }

    .input-container button:disabled {
        background: linear-gradient(135deg, var(--tum-gray), #d1d5db);
        cursor: not-allowed;
        transform: none;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    }

    /* Typing indicator */
    .typing-indicator {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        padding: 1rem 1.5rem;
        background: linear-gradient(135deg, #ffffff, #f8f9fa);
        border-radius: 1.5rem;
        margin-bottom: 1.5rem;
        animation: typingSlideIn 0.5s ease-out;
        align-self: flex-start;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(0, 100, 170, 0.1);
        max-width: 120px;
    }

    .typing-dot {
        width: 10px;
        height: 10px;
        background: linear-gradient(135deg, var(--tum-blue), var(--tum-light-blue));
        border-radius: 50%;
        animation: typingAnimation 1.4s infinite ease-in-out;
        box-shadow: 0 2px 8px rgba(0, 100, 170, 0.3);
    }

    .typing-dot:nth-child(1) { animation-delay: 0s; }
    .typing-dot:nth-child(2) { animation-delay: 0.2s; }
    .typing-dot:nth-child(3) { animation-delay: 0.4s; }

    /* Download button styling */
    .stDownloadButton {
        background: linear-gradient(135deg, var(--tum-success), #20c997) !important;
        border-radius: 1rem !important;
        padding: 0.75rem 1.5rem !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(40, 167, 69, 0.3) !important;
        border: none !important;
        color: white !important;
        font-weight: 600 !important;
    }

    .stDownloadButton:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(40, 167, 69, 0.4) !important;
    }

    /* Animations */
    @keyframes slideInDown {
        from {
            opacity: 0;
            transform: translateY(-30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    @keyframes slideInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    @keyframes messageSlideIn {
        from {
            opacity: 0;
            transform: translateY(20px) scale(0.95);
        }
        to {
            opacity: 1;
            transform: translateY(0) scale(1);
        }
    }

    @keyframes messageSlideInLeft {
        from {
            opacity: 0;
            transform: translateX(-30px) scale(0.95);
        }
        to {
            opacity: 1;
            transform: translateX(0) scale(1);
        }
    }

    @keyframes messageSlideInRight {
        from {
            opacity: 0;
            transform: translateX(30px) scale(0.95);
        }
        to {
            opacity: 1;
            transform: translateX(0) scale(1);
        }
    }

    @keyframes typingSlideIn {
        from {
            opacity: 0;
            transform: translateY(10px) scale(0.9);
        }
        to {
            opacity: 1;
            transform: translateY(0) scale(1);
        }
    }

    @keyframes typingAnimation {
        0%, 60%, 100% { 
            transform: translateY(0) scale(1);
            opacity: 1;
        }
        30% { 
            transform: translateY(-6px) scale(1.1);
            opacity: 0.8;
        }
    }

    @keyframes fadeIn {
        from { 
            opacity: 0; 
            transform: translateY(10px); 
        }
        to { 
            opacity: 1; 
            transform: translateY(0); 
        }
    }

    /* Pulse animation for loading states */
    @keyframes pulse {
        0%, 100% {
            opacity: 1;
        }
        50% {
            opacity: 0.5;
        }
    }

    .pulse {
        animation: pulse 2s infinite;
    }

    /* Floating animation for elements */
    @keyframes float {
        0%, 100% {
            transform: translateY(0px);
        }
        50% {
            transform: translateY(-10px);
        }
    }

    .float {
        animation: float 3s ease-in-out infinite;
    }

    /* Sidebar styling */
    .sidebar-content {
        padding: 1rem;
    }

    .sidebar-header {
        text-align: center;
        margin-bottom: 2rem;
        animation: slideInDown 0.8s ease-out;
    }

    .sidebar-header img {
        width: 150px;
        margin-bottom: 1rem;
        transition: all 0.3s ease;
        filter: drop-shadow(0 4px 15px rgba(0, 100, 170, 0.2));
    }

    .sidebar-header img:hover {
        transform: scale(1.05);
        filter: drop-shadow(0 8px 25px rgba(0, 100, 170, 0.3));
    }

    .history-item {
        background: linear-gradient(135deg, #ffffff, #f8f9fa);
        border: 1px solid rgba(0, 100, 170, 0.1);
        border-radius: 1rem;
        padding: 1.25rem;
        margin-bottom: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
        animation: fadeIn 0.5s ease-out;
    }

    .history-item:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
        border-color: rgba(0, 100, 170, 0.2);
    }

    .history-item-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.75rem;
    }

    .history-item-title {
        font-weight: 600;
        color: var(--tum-blue);
        font-size: 0.95rem;
    }

    .history-item-timestamp {
        color: var(--tum-dark-gray);
        font-size: 0.85rem;
        opacity: 0.8;
    }

    .history-item-content {
        color: var(--tum-dark-gray);
        font-size: 0.9rem;
        margin-bottom: 1rem;
        max-height: 100px;
        overflow-y: auto;
        line-height: 1.5;
    }

    .history-item-actions {
        display: flex;
        gap: 0.5rem;
    }

    .history-item-actions button {
        padding: 0.5rem 1rem;
        border-radius: 0.75rem;
        border: none;
        cursor: pointer;
        transition: all 0.3s ease;
        font-size: 0.9rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        background: linear-gradient(135deg, var(--tum-blue), var(--tum-light-blue));
        color: white;
        box-shadow: 0 2px 10px rgba(0, 100, 170, 0.2);
    }

    .history-item-actions button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(0, 100, 170, 0.3);
    }

    /* Responsive design */
    @media (max-width: 768px) {
        .chat-container {
            margin: 0.5rem;
            padding: 1rem;
        }
        
        .input-container {
            padding: 1rem;
        }
        
        .main h1 {
            font-size: 2rem;
            margin: 1rem 0;
        }
        
        .chat-message {
            max-width: 95%;
            padding: 1rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "current_document" not in st.session_state:
    st.session_state.current_document = None
if "document_history" not in st.session_state:
    st.session_state.document_history = []
if "is_generating" not in st.session_state:
    st.session_state.is_generating = False
if "typing" not in st.session_state:
    st.session_state.typing = False
if "input_key" not in st.session_state:
    st.session_state.input_key = 0
if "doc_counters" not in st.session_state:
    st.session_state.doc_counters = {}
if "exported_file" not in st.session_state:
    st.session_state.exported_file = None
if "exported_file_name" not in st.session_state:
    st.session_state.exported_file_name = None
if "exported_file_mime" not in st.session_state:
    st.session_state.exported_file_mime = None

# Backend URL
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

def generate_document(doc_type: str, tone: str, prompt: str, additional_context: str = ""):
    """
    Generate a document using the LLM service.

    Args:
        doc_type (str): The type of document to generate.
        tone (str): The tone to use in the document.
        prompt (str): The main prompt or key points for the document.
        additional_context (str, optional): Any additional context to include. Defaults to "".

    Return:
        dict or None: The response from the backend API, or None if an error occurs.
    """
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/documents/generate",
            json={
                "doc_type": doc_type,
                "tone": tone,
                "prompt": prompt,
                "additional_context": additional_context
            }
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error generating document: {str(e)}")
        return None

def export_document_and_prepare_download(document, format, doc_type, tone):
    """
    Export a document in the specified format and prepare it for download.

    Args:
        document (str): The document content to export.
        format (str): The export format (e.g., 'pdf', 'docx', 'txt').
        doc_type (str): The type of document.
        tone (str): The tone of the document.

    Return:
        None. Sets session state variables for the exported file.
    """
    metadata = {"doc_type": doc_type or "Document", "tone": tone or "Neutral"}
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/documents/export",
            json={
                "document_content": document,
                "format": format,
                "metadata": metadata
            }
        )
        response.raise_for_status()
        file_bytes = response.content
        file_ext = format.lower()
        file_name = f"TUM_{doc_type}_{tone}.{file_ext}"
        mime = {
            "pdf": "application/pdf",
            "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "txt": "text/plain"
        }.get(file_ext, "application/octet-stream")
        st.session_state.exported_file = file_bytes
        st.session_state.exported_file_name = file_name
        st.session_state.exported_file_mime = mime
    except Exception as e:
        st.error(f"Error exporting document: {str(e)}")
        st.session_state.exported_file = None
        st.session_state.exported_file_name = None
        st.session_state.exported_file_mime = None

def simulate_streaming(text: str, chunk_size: int = 10):
    """
    Simulate streaming text by yielding chunks.

    Args:
        text (str): The text to stream.
        chunk_size (int, optional): The size of each chunk. Defaults to 10.

    Return:
        generator: Yields chunks of the text.
    """
    for i in range(0, len(text), chunk_size):
        yield text[i:i + chunk_size]
        time.sleep(0.02)  # Small delay for smooth animation

# Document Preview Modal state
if "show_preview" not in st.session_state:
    st.session_state.show_preview = False
if "preview_doc_idx" not in st.session_state:
    st.session_state.preview_doc_idx = None

def open_preview(idx):
    """
    Open the document preview modal for a given document index.

    Args:
        idx (int): The index of the document in history to preview.

    Return:
        None. Updates session state to show the preview modal.
    """
    st.session_state.show_preview = True
    st.session_state.preview_doc_idx = idx

def close_preview():
    """
    Close the document preview modal.

    Args:
        None

    Return:
        None. Updates session state to hide the preview modal.
    """
    st.session_state.show_preview = False
    st.session_state.preview_doc_idx = None

# Helper to fetch and return file bytes for download
def get_exported_file_bytes(document, format, doc_type, tone):
    """
    Fetch and return file bytes for download from the backend export endpoint.

    Args:
        document (str): The document content to export.
        format (str): The export format (e.g., 'pdf', 'docx', 'txt').
        doc_type (str): The type of document.
        tone (str): The tone of the document.

    Return:
        bytes or None: The file bytes if successful, or None if an error occurs.
    """
    metadata = {"doc_type": doc_type or "Document", "tone": tone or "Neutral"}
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/documents/export",
            json={
                "document_content": document,
                "format": format,
                "metadata": metadata
            }
        )
        response.raise_for_status()
        return response.content
    except Exception as e:
        st.error(f"Error exporting document: {str(e)}")
        return None

def refine_document(current_document: str, refinement_prompt: str, doc_type: str, tone: str, history=None):
    """
    Refine a document using the LLM service, with up to the last 3 documents as history.

    Args:
        current_document (str): The document to be refined.
        refinement_prompt (str): The user's instruction for refinement.
        doc_type (str): The type of document.
        tone (str): The tone to use in the document.
        history (list, optional): List of previous document contents for context. Defaults to None.

    Return:
        str or None: The refined document as a string, or None if an error occurs.
    """
    try:
        payload = {
            "current_document": current_document,
            "refinement_prompt": refinement_prompt,
            "doc_type": doc_type,
            "tone": tone
        }
        if history:
            payload["history"] = history
        response = requests.post(
            f"{BACKEND_URL}/api/documents/refine",
            json=payload,
            stream=True
        )
        response.raise_for_status()
        # Stream the response
        full_response = ""
        for line in response.iter_lines():
            if line:
                try:
                    chunk = json.loads(line.decode().replace('data: ', ''))
                    full_response += chunk["document"]
                except Exception:
                    continue
        return full_response
    except Exception as e:
        st.error(f"Error refining document: {str(e)}")
        return None

# Sidebar for document type and tone selection
with st.sidebar:
    st.markdown('<div class="sidebar-header">', unsafe_allow_html=True)
    st.image("https://upload.wikimedia.org/wikipedia/commons/c/c8/Logo_of_the_Technical_University_of_Munich.svg", 
             width=150)
    
    st.markdown("### Document Settings")
    doc_type = st.selectbox(
        "📄 Document Type",
        options=[dt.value for dt in DocumentType],
        format_func=lambda x: x.replace("_", " ").title()
    )
    tone = st.selectbox(
        "🎭 Tone",
        options=[t.value for t in ToneType],
        format_func=lambda x: x.replace("_", " ").title()
    )
    
    st.markdown("---")
    st.markdown("### 📜 Document History")

    # Count documents per (type, tone)
    doc_counts = {}
    for doc in st.session_state.document_history:
        key = (doc.get('type', 'Unknown'), doc.get('tone', 'Neutral'))
        doc_counts[key] = doc_counts.get(key, 0) + 1
        doc['doc_number'] = doc_counts[key]

    for idx, doc in enumerate(reversed(st.session_state.document_history)):
        title = f"[{doc.get('type', 'Unknown')}_{doc.get('tone', 'Neutral')}_{doc['doc_number']}]"
        st.markdown(f"""
        <div class="history-item">
            <div class="history-item-header">
                <span class="history-item-title">{title}</span>
            </div>
            <div class="history-item-content">{doc['content'][:200]}{'...' if len(doc['content']) > 200 else ''}</div>
            <div class="history-item-actions">
        """, unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1,1,1])
        with col1:
            if st.button("👁️ Preview", key=f"preview_{idx}", on_click=open_preview, args=(idx,)):
                pass
        with col2:
            file_bytes = get_exported_file_bytes(doc['content'], 'pdf', doc.get('type'), doc.get('tone'))
            if file_bytes:
                st.download_button(
                    label="📑 PDF",
                    data=file_bytes,
                    file_name=f"TUM_{doc.get('type', 'Document')}_{doc.get('tone', 'Neutral')}.pdf",
                    mime="application/pdf",
                    key=f"download_pdf_{idx}"
                )
        with col3:
            file_bytes = get_exported_file_bytes(doc['content'], 'docx', doc.get('type'), doc.get('tone'))
            if file_bytes:
                st.download_button(
                    label="📘 DOCX",
                    data=file_bytes,
                    file_name=f"TUM_{doc.get('type', 'Document')}_{doc.get('tone', 'Neutral')}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    key=f"download_docx_{idx}"
                )
        st.markdown("</div></div>", unsafe_allow_html=True)

# Show download button if a file is ready
if st.session_state.exported_file:
    st.download_button(
        label=f"Download {st.session_state.exported_file_name}",
        data=st.session_state.exported_file,
        file_name=st.session_state.exported_file_name,
        mime=st.session_state.exported_file_mime,
        key="download_btn"
    )

# Document Preview Modal
if st.session_state.show_preview and st.session_state.preview_doc_idx is not None:
    doc = st.session_state.document_history[-(st.session_state.preview_doc_idx+1)]
    st.markdown(f"""
    <div class="modal" style="display: block;">
        <div class="modal-content" style="background: #fff; border-radius: 1rem; max-width: 700px; margin: 5% auto; padding: 2rem; box-shadow: 0 4px 20px rgba(0,0,0,0.15); max-height: 80vh; overflow-y: auto;">
            <div style="display: flex; justify-content: flex-end;">
                <button class="close-button" onclick="window.dispatchEvent(new CustomEvent('closePreview'))" style="background: none; border: none; font-size: 1.5rem; cursor: pointer; color: #333;">×</button>
            </div>
            <div class="document-preview" style="white-space: pre-wrap; line-height: 1.6; font-size: 1.1rem; color: #222;">
                {doc['content']}
            </div>
            <div class="preview-actions" style="display: flex; gap: 1rem; margin-top: 1rem; justify-content: flex-end;">
                <button class="primary" onclick="exportDocument('{doc['content']}', 'pdf')">📑 Export PDF</button>
                <button class="primary" onclick="exportDocument('{doc['content']}', 'docx')">📘 Export DOCX</button>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.button("Close Preview", on_click=close_preview, key="close_preview_btn")

# Main chat interface
st.title("TUM Admin Assistant 🤖")

# Chat container
chat_container = st.container()

# Display chat messages
with chat_container:
    for message in st.session_state.messages:
        st.markdown(f"""
        <div class="chat-message {message['role']}">
            <div class="content">
                <div class="avatar">{'👤' if message['role'] == 'user' else '🤖'}</div>
                <div class="message">{message['content']}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Show typing indicator if generating
    if st.session_state.typing:
        st.markdown("""
        <div class="typing-indicator">
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
        </div>
        """, unsafe_allow_html=True)

# Input container
with st.container():
    st.markdown('<div class="input-container">', unsafe_allow_html=True)
    prompt = st.text_area("", placeholder="Type your message here...", key=f"prompt_input_{st.session_state.input_key}", height=50)
    if st.button("Send ✉️", key="send_button", disabled=st.session_state.is_generating):
        if prompt:
            st.session_state.is_generating = True
            st.session_state.typing = True
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.spinner(""):
                # If there is a previous document, treat as refinement
                if st.session_state.document_history:
                    last_doc = st.session_state.document_history[-1]
                    doc_type_val = last_doc.get("type", doc_type)
                    tone_val = last_doc.get("tone", tone)
                    # Get up to the last 3 documents as history (excluding the current one)
                    history_docs = [d["content"] for d in st.session_state.document_history[-3:]]
                    refined = refine_document(last_doc["content"], prompt, doc_type_val, tone_val, history=history_docs)
                    if refined:
                        message_placeholder = st.empty()
                        full_response = ""
                        for chunk in simulate_streaming(refined):
                            full_response += chunk
                            message_placeholder.markdown(f"""
                            <div class=\"chat-message assistant\">\n<div class=\"content\">\n<div class=\"avatar\">🤖</div>\n<div class=\"message\">{full_response}</div>\n</div>\n</div>\n""", unsafe_allow_html=True)
                        st.session_state.current_document = refined
                        st.session_state.messages.append({"role": "assistant", "content": refined})
                        st.session_state.document_history.append({
                            "type": doc_type_val,
                            "tone": tone_val,
                            "content": refined,
                            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        })
                else:
                    # No previous document, generate new
                    result = generate_document(doc_type, tone, prompt)
                    if result:
                        message_placeholder = st.empty()
                        full_response = ""
                        for chunk in simulate_streaming(result["document"]):
                            full_response += chunk
                            message_placeholder.markdown(f"""
                            <div class=\"chat-message assistant\">\n<div class=\"content\">\n<div class=\"avatar\">🤖</div>\n<div class=\"message\">{full_response}</div>\n</div>\n</div>\n""", unsafe_allow_html=True)
                        st.session_state.current_document = result["document"]
                        st.session_state.messages.append({"role": "assistant", "content": result["document"]})
                        st.session_state.document_history.append({
                            "type": doc_type,
                            "tone": tone,
                            "content": result["document"],
                            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        })
            st.session_state.is_generating = False
            st.session_state.typing = False
            st.session_state.input_key += 1
            st.experimental_rerun()
    st.markdown('</div>', unsafe_allow_html=True) 