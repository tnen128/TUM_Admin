import streamlit as st
import requests
from dotenv import load_dotenv
import os
import base64
from datetime import datetime

# Load environment variables
load_dotenv()

# Custom CSS
def load_custom_css():
    st.markdown("""
        <style>
        /* Main container styling */
        .main {
            padding: 2rem;
        }
        
        /* Custom title styling */
        .custom-title {
            color: #0064AA;
            font-size: 2.5rem;
            font-weight: bold;
            margin-bottom: 2rem;
            text-align: center;
            padding: 1rem;
            border-bottom: 3px solid #0064AA;
        }
        
        /* Card styling */
        .stTextArea > div > div {
            border-radius: 10px !important;
            border: 1px solid #0064AA !important;
        }
        
        /* Button styling */
        .stButton > button {
            border-radius: 20px;
            padding: 0.5rem 2rem;
            background-color: #0064AA;
            color: white;
            border: none;
            transition: all 0.3s ease;
        }
        
        .stButton > button:hover {
            background-color: #003359;
            transform: translateY(-2px);
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        /* Sidebar styling */
        .css-1d391kg {
            padding: 2rem 1rem;
        }
        
        /* Status badges */
        .status-badge {
            padding: 0.3rem 1rem;
            border-radius: 15px;
            font-size: 0.8rem;
            font-weight: bold;
            margin: 0.5rem 0;
            display: inline-block;
        }
        
        .status-success {
            background-color: #e6f3e6;
            color: #2e7d32;
            border: 1px solid #2e7d32;
        }
        
        .status-info {
            background-color: #e3f2fd;
            color: #1976d2;
            border: 1px solid #1976d2;
        }
        
        /* Document preview styling */
        .document-preview {
            background-color: white;
            padding: 2rem;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin: 1rem 0;
        }
        
        /* Export options styling */
        .export-option {
            text-align: center;
            padding: 1rem;
            border-radius: 10px;
            background-color: #f5f5f5;
            transition: all 0.3s ease;
        }
        
        .export-option:hover {
            background-color: #e0e0e0;
            transform: translateY(-2px);
        }
        
        /* History timeline */
        .timeline-item {
            border-left: 2px solid #0064AA;
            padding-left: 1rem;
            margin: 1rem 0;
            position: relative;
        }
        
        .timeline-item::before {
            content: '';
            width: 12px;
            height: 12px;
            background-color: #0064AA;
            border-radius: 50%;
            position: absolute;
            left: -7px;
            top: 0;
        }
        </style>
    """, unsafe_allow_html=True)

class AdminInterface:
    def __init__(self):
        self.api_url = os.getenv("BACKEND_URL", "http://localhost:8000")
        self.setup_page()
        self.initialize_session()
        load_custom_css()

    def setup_page(self):
        st.set_page_config(
            page_title="TUM Admin Assistant",
            page_icon="📝",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        st.markdown('<h1 class="custom-title">TUM Admin</h1>', unsafe_allow_html=True)

    def initialize_session(self):
        if "current_document" not in st.session_state:
            st.session_state.current_document = None
        if "history" not in st.session_state:
            st.session_state.history = []
        if "metadata" not in st.session_state:
            st.session_state.metadata = {}

    def render_sidebar(self):
        with st.sidebar:
            st.image("https://upload.wikimedia.org/wikipedia/commons/c/c8/Logo_of_the_Technical_University_of_Munich.svg", 
                    width=200)
            
            st.markdown("### Document Settings")
            
            doc_type = st.selectbox(
                "📄 Document Type",
                ["Announcement", "Student Communication", "Meeting Summary"],
                help="Select the type of document you want to generate"
            )
            
            tone = st.selectbox(
                "🎭 Tone",
                ["Neutral", "Friendly", "Firm but polite", "Formal"],
                help="Choose the tone of voice for your document"
            )
            
            st.markdown("---")
            
            if st.session_state.history:
                st.markdown("### 📜 Document History")
                for idx, entry in enumerate(reversed(st.session_state.history)):
                    with st.expander(f"Version {len(st.session_state.history) - idx}"):
                        st.markdown(f'<div class="timeline-item">{entry["assistant"]}</div>', 
                                  unsafe_allow_html=True)
            
            return doc_type, tone

    def render_export_options(self):
        st.markdown("### 📤 Export Options")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            with st.container():
                st.markdown('<div class="export-option">', unsafe_allow_html=True)
                if st.button("📑 Export as PDF"):
                    self.export_document("pdf")
                st.markdown("Professional PDF with TUM branding")
                st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            with st.container():
                st.markdown('<div class="export-option">', unsafe_allow_html=True)
                if st.button("📘 Export as DOCX"):
                    self.export_document("docx")
                st.markdown("Editable Microsoft Word format")
                st.markdown('</div>', unsafe_allow_html=True)
        
        with col3:
            with st.container():
                st.markdown('<div class="export-option">', unsafe_allow_html=True)
                if st.button("📝 Export as TXT"):
                    self.export_document("txt")
                st.markdown("Simple text format")
                st.markdown('</div>', unsafe_allow_html=True)

    def render_main_content(self, doc_type: str, tone: str):
        if not st.session_state.current_document:
            st.markdown("### 🎯 Generate New Document")
            prompt = st.text_area(
                "What kind of document do you need?",
                height=150,
                placeholder="e.g., Write an announcement about the extended registration deadline...",
                help="Describe the document you need, including key points and any specific requirements"
            )
            
            col1, col2 = st.columns([1, 4])
            with col1:
                if st.button("✨ Generate Document", use_container_width=True):
                    with st.spinner("Generating your document..."):
                        self.generate_document(prompt, doc_type, tone)
        
        if st.session_state.current_document:
            st.markdown("### 📄 Current Document")
            st.markdown('<div class="document-preview">', unsafe_allow_html=True)
            st.markdown(f"""
                <div class="status-badge status-info">Type: {st.session_state.metadata.get('doc_type', 'Document')}</div>
                <div class="status-badge status-info">Tone: {st.session_state.metadata.get('tone', 'Standard')}</div>
            """, unsafe_allow_html=True)
            
            st.text_area(
                "",
                st.session_state.current_document,
                height=300,
                disabled=True
            )
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Add export options
            self.render_export_options()
            
            st.markdown("### 🔄 Refine Document")
            refinement = st.text_area(
                "How would you like to refine this document?",
                height=100,
                placeholder="e.g., Make it more formal...",
                help="Provide instructions for how you'd like to improve the document"
            )
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✏️ Refine Document", use_container_width=True):
                    with st.spinner("Refining your document..."):
                        self.refine_document(refinement)
            with col2:
                if st.button("🔄 Start New Document", use_container_width=True):
                    self.reset_session()

    def generate_document(self, prompt: str, doc_type: str, tone: str):
        try:
            response = requests.post(
                f"{self.api_url}/api/documents/generate",
                json={
                    "prompt": prompt,
                    "doc_type": doc_type,
                    "tone": tone
                }
            )
            response.raise_for_status()
            data = response.json()
            
            st.session_state.current_document = data["document"]
            st.session_state.metadata = data["metadata"]
            st.session_state.history = data.get("history", [])
            st.experimental_rerun()
        except Exception as e:
            st.error(f"Error generating document: {str(e)}")

    def refine_document(self, refinement_prompt: str):
        try:
            response = requests.post(
                f"{self.api_url}/api/documents/refine",
                json={"refinement_prompt": refinement_prompt}
            )
            response.raise_for_status()
            data = response.json()
            
            st.session_state.current_document = data["document"]
            st.session_state.metadata.update(data.get("metadata", {}))
            st.session_state.history = data.get("history", [])
            st.experimental_rerun()
        except Exception as e:
            st.error(f"Error refining document: {str(e)}")

    def export_document(self, format: str):
        try:
            with st.spinner(f"Preparing {format.upper()} export..."):
                response = requests.post(
                    f"{self.api_url}/api/documents/export",
                    json={
                        "format": format,
                        "document_content": st.session_state.current_document,
                        "metadata": st.session_state.metadata
                    }
                )
                response.raise_for_status()
                
                # Get the filename from the Content-Disposition header
                content_disposition = response.headers.get('Content-Disposition', '')
                filename = content_disposition.split('filename=')[-1].strip('"')
                if not filename:
                    filename = f"tum_document_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{format}"
                
                # Create download button with custom styling
                st.download_button(
                    label=f"📥 Download {format.upper()} File",
                    data=response.content,
                    file_name=filename,
                    mime=response.headers.get('Content-Type', f'application/{format}'),
                    key=f"download_{format}_{datetime.now().strftime('%H%M%S')}"
                )
                st.success(f"Document successfully exported as {format.upper()}")
        except Exception as e:
            st.error(f"Error exporting document: {str(e)}")
            # Log the full error for debugging
            print(f"Export error details: {str(e)}")

    def reset_session(self):
        st.session_state.current_document = None
        st.session_state.metadata = {}
        st.session_state.history = []
        st.experimental_rerun()

    def run(self):
        doc_type, tone = self.render_sidebar()
        self.render_main_content(doc_type, tone)

if __name__ == "__main__":
    app = AdminInterface()
    app.run() 