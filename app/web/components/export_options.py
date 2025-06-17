"""
Export options component for document export functionality.
"""
import streamlit as st
from typing import Callable
from app.web.utils.styles import get_export_card

def render_export_options(export_callback: Callable[[str], None]) -> None:
    """Render export format options with descriptions."""
    st.markdown("### 📤 Export Options")
    
    col1, col2, col3 = st.columns(3)
    
    export_formats = [
        {
            "format": "pdf",
            "title": "PDF",
            "description": "Professional PDF with TUM branding"
        },
        {
            "format": "docx",
            "title": "DOCX",
            "description": "Editable Microsoft Word format"
        },
        {
            "format": "txt",
            "title": "TXT",
            "description": "Simple text format"
        }
    ]
    
    for col, format_info in zip([col1, col2, col3], export_formats):
        with col:
            with st.container():
                st.markdown(
                    get_export_card(
                        format_info["format"],
                        format_info["description"]
                    ),
                    unsafe_allow_html=True
                )
                if st.button(
                    f"Export as {format_info['title']}",
                    key=f"export_{format_info['format']}"
                ):
                    export_callback(format_info["format"]) 