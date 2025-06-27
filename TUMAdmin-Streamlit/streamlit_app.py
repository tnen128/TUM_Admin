import streamlit as st
import requests
# from dotenv import load_dotenv
import os
import base64
from datetime import datetime
import json
from typing import Dict, Any
import time
from app.api.models.document import DocumentType, ToneType
import io

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
    }

    /* Main container styling */
    .main {
        padding: 0;
        background-color: #f8f9fa;
        height: 100vh;
        display: flex;
        flex-direction: column;
    }

    .stApp {
        max-width: 100%;
        padding: 0;
        height: 100vh;
    }

    /* Chat container */
    .chat-container {
        flex: 1;
        overflow-y: auto;
        padding: 1rem;
        margin-bottom: 80px; /* Space for input container */
        display: flex;
        flex-direction: column;
    }

    /* Chat messages */
    .chat-message {
        padding: 1.5rem;
        border-radius: 1rem;
        margin-bottom: 1rem;
        max-width: 80%;
        display: flex;
        flex-direction: column;
        animation: fadeInUp 0.5s cubic-bezier(0.23, 1, 0.32, 1);
        transition: box-shadow 0.2s, transform 0.2s;
    }

    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(30px) scale(0.98); }
        to { opacity: 1; transform: translateY(0) scale(1); }
    }

    .chat-message.user {
        background-color: var(--tum-blue);
        color: white;
        margin-left: auto;
        border-bottom-right-radius: 0.25rem;
    }

    .chat-message.assistant {
        background-color: var(--tum-gray);
        color: var(--tum-dark-gray);
        margin-right: auto;
        border-bottom-left-radius: 0.25rem;
    }

    .chat-message .content {
        display: flex;
        align-items: flex-start;
        gap: 0.75rem;
    }

    .chat-message .avatar {
        width: 36px;
        height: 36px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.2rem;
        background-color: white;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
        flex-shrink: 0;
    }

    .chat-message .message {
        flex: 1;
        white-space: pre-wrap;
        line-height: 1.6;
        font-size: 1rem;
    }

    /* Input container */
    .input-container {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        padding: 1rem;
        background-color: white;
        border-top: 1px solid var(--tum-gray);
        display: flex;
        gap: 1rem;
        align-items: center;
        box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.05);
        z-index: 100;
    }

    .input-container textarea {
        flex: 1;
        background-color: white;
        color: var(--tum-dark-gray);
        border: 2px solid var(--tum-gray);
        border-radius: 1rem;
        padding: 0.75rem 1rem;
        resize: none;
        height: 50px;
        transition: all 0.3s ease;
        font-size: 1rem;
        line-height: 1.5;
    }

    .input-container textarea:focus {
        border-color: var(--tum-blue);
        box-shadow: 0 0 0 2px rgba(0, 100, 170, 0.1);
        outline: none;
    }

    .input-container button {
        background-color: var(--tum-blue);
        color: white;
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: 1rem;
        cursor: pointer;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        transition: all 0.3s ease;
        font-weight: 600;
        font-size: 1rem;
        height: 50px;
    }

    .input-container button:hover {
        background-color: var(--tum-light-blue);
        transform: translateY(-1px);
    }

    .input-container button:disabled {
        background-color: var(--tum-gray);
        cursor: not-allowed;
        transform: none;
    }

    /* Typing indicator */
    .typing-indicator {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.5rem 1rem;
        background-color: var(--tum-gray);
        border-radius: 1rem;
        margin-bottom: 1rem;
        animation: fadeIn 0.3s ease-in-out;
        align-self: flex-start;
    }

    .typing-dot {
        width: 8px;
        height: 8px;
        background-color: var(--tum-blue);
        border-radius: 50%;
        animation: typingAnimation 1.4s infinite ease-in-out;
    }

    .typing-dot:nth-child(1) { animation-delay: 0s; }
    .typing-dot:nth-child(2) { animation-delay: 0.2s; }
    .typing-dot:nth-child(3) { animation-delay: 0.4s; }

    @keyframes typingAnimation {
        0%, 60%, 100% { transform: translateY(0); }
        30% { transform: translateY(-4px); }
    }

    /* Sidebar styling */
    .sidebar-content {
        padding: 1rem;
        animation: sidebarSlideIn 0.7s cubic-bezier(0.23, 1, 0.32, 1);
    }

    .sidebar-header {
        text-align: center;
        margin-bottom: 2rem;
    }

    .sidebar-header img {
        width: 150px;
        margin-bottom: 1rem;
    }

    .history-item {
        background-color: white;
        border: 1px solid var(--tum-gray);
        border-radius: 0.75rem;
        padding: 1rem;
        margin-bottom: 1rem;
        transition: all 0.3s ease;
        animation: fadeInCard 0.6s cubic-bezier(0.23, 1, 0.32, 1);
    }

    .history-item:hover {
        transform: translateY(-2px) scale(1.01);
        box-shadow: 0 8px 32px rgba(0, 100, 170, 0.10);
    }

    .history-item-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.5rem;
    }

    .history-item-title {
        font-weight: 600;
        color: var(--tum-blue);
    }

    .history-item-timestamp {
        color: var(--tum-dark-gray);
        font-size: 0.9rem;
    }

    .history-item-content {
        color: var(--tum-dark-gray);
        font-size: 0.9rem;
        margin-bottom: 1rem;
        max-height: 100px;
        overflow-y: auto;
    }

    .history-item-actions {
        display: flex;
        gap: 0.5rem;
    }

    .history-item-actions button {
        padding: 0.5rem 1rem;
        border-radius: 0.5rem;
        border: none;
        cursor: pointer;
        transition: all 0.3s ease;
        font-size: 0.9rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    .history-item-actions button:hover {
        transform: translateY(-1px);
    }

    /* Animations for chat messages */
    .chat-message:hover {
        box-shadow: 0 8px 32px rgba(0, 100, 170, 0.10);
        transform: translateY(-2px) scale(1.01);
    }

    /* Button hover/press animation */
    .stButton > button, .stDownloadButton {
        transition: background 0.2s, box-shadow 0.2s, transform 0.15s;
    }
    .stButton > button:hover, .stDownloadButton:hover {
        box-shadow: 0 4px 16px rgba(0, 100, 170, 0.15);
        transform: translateY(-2px) scale(1.03);
    }
    .stButton > button:active, .stDownloadButton:active {
        transform: scale(0.98);
    }

    /* Sidebar slide-in animation */
    @keyframes sidebarSlideIn {
        from { opacity: 0; transform: translateX(-40px); }
        to { opacity: 1; transform: translateX(0); }
    }

    /* Document history card animation */
    @keyframes fadeInCard {
        from { opacity: 0; transform: translateY(20px) scale(0.98); }
        to { opacity: 1; transform: translateY(0) scale(1); }
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

def generate_document(doc_type: str, tone: str, prompt: str, additional_context: str = "", sender_name: str = "", sender_profession: str = "", language: str = "English"):
    """
    Generate a document using the LLM service.

    Args:
        doc_type (str): The type of document to generate.
        tone (str): The tone to use in the document.
        prompt (str): The main prompt or key points for the document.
        additional_context (str, optional): Any additional context to include. Defaults to "".
        sender_name (str, optional): The sender's name. Defaults to "".
        sender_profession (str, optional): The sender's profession. Defaults to "".
        language (str, optional): The language of the email. Defaults to "English".

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
                "additional_context": additional_context,
                "sender_name": sender_name,
                "sender_profession": sender_profession,
                "language": language
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
    st.image("https://upload.wikimedia.org/wikipedia/commons/c/c8/Logo_of_the_Technical_University_of_Munich.svg", width=150)
    
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
    sender_name = st.text_input("Sender Name", value="")
    sender_profession = st.text_input("Sender Profession", value="")
    language = st.selectbox("Language", options=["English", "German", "Both"], index=0)
    
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
    st.markdown(
        f'''<div style="background: #23272b; border-radius: 1.2rem; box-shadow: 0 12px 48px rgba(0,100,170,0.22); max-width: 900px; margin: 3% auto 2rem auto; padding: 2.7rem 2.5rem 2.2rem 2.5rem; border: 2.5px solid #0064AA;">
        <div style="font-size: 1.5rem; font-weight: 800; color: #fff; letter-spacing: 0.5px; margin-bottom: 1.5rem; text-align: left;">
            📢 Announcement Preview
        </div>
        <div style="background: #181c20; border-radius: 0.9rem; padding: 1.6rem 1.3rem; color: #f5f5f5; font-size: 1.18rem; line-height: 1.8; min-height: 260px; max-height: 600px; overflow-y: auto; white-space: pre-wrap; border: 1px solid #333;">
        {doc['content'].replace('<','&lt;').replace('>','&gt;').rstrip('</div>').rstrip()}</div></div>''',
        unsafe_allow_html=True
    )
    st.button("Close Preview", on_click=close_preview, key="close_preview_btn", help="Close this preview")

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
                    # Send the full document history for context
                    history_docs = [d["content"] for d in st.session_state.document_history]
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
                    result = generate_document(doc_type, tone, prompt, sender_name=sender_name, sender_profession=sender_profession, language=language)
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