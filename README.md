# TUM Admin Assistant

## Overview
TUM Admin Assistant is a robust, secure, and user-friendly system for generating, refining, and exporting official administrative documents for the Technical University of Munich (TUM). It leverages LLMs (Google Gemini) and LangChain for context-aware document creation and refinement, with a modern Streamlit frontend.

## Features
- Generate announcements, student communications, and meeting summaries with selectable tone
- Refine documents using conversational context (up to last 3 documents)
- Export documents as PDF, DOCX, or TXT with TUM branding
- Chat-like interface for easy interaction
- Robust prompt-injection protection and input validation
- Session management and document history

## Installation
1. Clone the repository:
   ```bash
   git clone <repo-url>
   cd TUMAdmin
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up your `.env` file with your Gemini API key and backend URL:
   ```env
   BACKEND_URL=http://localhost:8000
   GOOGLE_API_KEY=your_gemini_api_key_here
   ```

## Running the System
- **Backend:**
  ```bash
  export PYTHONPATH=$PYTHONPATH:$(pwd)
  uvicorn app.api.main:app --reload
  ```
- **Frontend:**
  ```bash
  streamlit run app/web/main.py
  ```

## API Endpoints
- `/api/documents/generate` — Generate a new document
- `/api/documents/refine` — Refine an existing document (with up to last 3 documents as context)
- `/api/documents/export` — Export a document in PDF, DOCX, or TXT format
- `/health` — Health check

## Document Generation & Refinement
- **Generation:** Uses a prompt template based on document type and tone. No previous context is used.
- **Refinement:** Uses a universal template that includes the last document and up to 2 more previous documents as context, plus the user's instruction. The LLM is instructed to only make the requested changes.

## Export Functionality
- Export any document in PDF, DOCX, or TXT format with TUM branding.
- Download is available directly from the sidebar for each document.

## Security & Robustness
- Hardened prompt templates to prevent prompt injection/jailbreaking
- Input validation and error handling
- Backend and frontend separation for API key security

## Example Usage
1. Generate an announcement:
   - "Please write an announcement for students: no lecture tomorrow for GenAI course. My name is Prof. Mohamed."
2. Refine the document:
   - "Change my name to Prof. Mostafa."
3. Export the document as PDF or DOCX from the sidebar.

## Resetting the Conversation
- To start fresh, simply refresh the Streamlit page. (A reset button can be added if desired.)

## Developer Notes
- All functions and endpoints are documented with detailed docstrings.
- The system is designed for extensibility and security.

## License
MIT
