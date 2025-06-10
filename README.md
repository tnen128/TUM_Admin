# TUM Administrative Document Assistant

A powerful tool for generating and managing administrative documents at TUM.

## Features

- **Document Generation**: Create various types of administrative documents:
  - Announcements
  - Student Communications
  - Meeting Summaries

- **Tone Control**: Customize document tone:
  - Neutral
  - Friendly
  - Firm but polite
  - Formal

- **Document Export**: Export documents in multiple formats:
  - PDF (with TUM branding)
  - DOCX (Microsoft Word)
  - TXT (Plain text)

- **Document Refinement**: Iteratively improve documents based on feedback
- **Version History**: Track changes and previous versions

## Setup

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file:
   ```
   BACKEND_URL=http://localhost:8000
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