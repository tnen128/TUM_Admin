"""
Utility functions for styling and theming the TUM Admin Assistant web interface.
"""

# TUM Brand Colors
TUM_COLORS = {
    'blue': '#0064AA',
    'dark_blue': '#003359',
    'light_blue': '#E3F2FD',
    'white': '#FFFFFF',
    'gray': '#F5F5F5',
    'dark_gray': '#E0E0E0',
    'success': '#2E7D32',
    'info': '#1976D2',
}

def get_icon(icon_type: str) -> str:
    """Return emoji icon based on type."""
    icons = {
        'document': '📄',
        'tone': '🎭',
        'export': '📤',
        'generate': '✨',
        'refine': '✏️',
        'reset': '🔄',
        'pdf': '📑',
        'docx': '📘',
        'txt': '📝',
        'download': '📥',
        'history': '📜',
        'target': '🎯',
    }
    return icons.get(icon_type, '')

def format_timestamp(timestamp: str) -> str:
    """Format timestamp for display."""
    from datetime import datetime
    try:
        dt = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
        return dt.strftime("%B %d, %Y at %I:%M %p")
    except:
        return timestamp

def get_status_badge(text: str, badge_type: str = 'info') -> str:
    """Generate HTML for a status badge."""
    return f'<div class="status-badge status-{badge_type}">{text}</div>'

def get_export_card(format_type: str, description: str) -> str:
    """Generate HTML for an export format card."""
    icon = get_icon(format_type.lower())
    return f"""
    <div class="export-option">
        <div class="export-icon">{icon}</div>
        <div class="export-title">{format_type.upper()}</div>
        <div class="export-description">{description}</div>
    </div>
    """ 