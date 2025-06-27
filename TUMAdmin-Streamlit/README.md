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

## Running the Application

1. Start the backend server:
   ```bash
   cd app/api
   uvicorn main:app --reload
   ```

2. Start the frontend (in a new terminal):
   ```bash
   cd app/web
   streamlit run main.py
   ```

The application will be available at:
- Frontend: http://localhost:8501
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## Project Structure

```
app/
├── api/
│   ├── models/
│   │   └── document.py
│   ├── services/
│   │   └── export_service.py
│   └── main.py
└── web/
    ├── components/
    ├── utils/
    └── main.py
```

## Usage

1. Select document type and tone from the sidebar
2. Enter your document requirements in the text area
3. Click "Generate Document" to create the initial version
4. Use the refinement options to improve the document
5. Export the final document in your preferred format

## Contributing

Please follow these steps to contribute:
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
