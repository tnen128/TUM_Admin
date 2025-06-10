"""
Document preview component for displaying generated documents.
"""
import streamlit as st
from typing import Dict, Optional
from app.web.utils.styles import get_status_badge, format_timestamp

def render_document_preview(
    content: str,
    metadata: Dict[str, str],
    created_at: Optional[str] = None
) -> None:
    """Render a document preview with metadata and content."""
    st.markdown('<div class="document-preview">', unsafe_allow_html=True)
    
    # Render metadata badges
    st.markdown(
        f"""
        {get_status_badge(f"Type: {metadata.get('doc_type', 'Document')}")}
        {get_status_badge(f"Tone: {metadata.get('tone', 'Standard')}")}
        """,
        unsafe_allow_html=True
    )
    
    if created_at:
        st.markdown(
            f"""
            {get_status_badge(f"Created: {format_timestamp(created_at)}", "success")}
            """,
            unsafe_allow_html=True
        )
    
    # Render document content
    st.text_area(
        "",
        content,
        height=300,
        disabled=True
    )
    
    st.markdown('</div>', unsafe_allow_html=True) 