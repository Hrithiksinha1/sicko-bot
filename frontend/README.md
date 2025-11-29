# Sicko Bot Frontend

Streamlit-based frontend for the Sicko Bot RAG-enabled chatbot.

## Features

1. **RAG Enabled Chatbot** - Chat with context from uploaded PDFs
2. **PDF Management** - Upload, delete, and update PDF files
3. **Citations** - All responses include source citations
4. **File Listing** - View all uploaded PDF files with chunk counts
5. **Multi-turn Conversations** - Maintains conversation context

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Make sure the backend server is running:
```bash
cd backend
python main.py
```

3. Run the Streamlit app:
```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## Usage

1. **Upload PDFs**: Use the sidebar to upload PDF files
2. **Chat**: Ask questions in the chat interface
3. **View Citations**: Expand citations to see source information
4. **Manage Files**: Delete or update files from the sidebar
5. **Clear Conversation**: Reset conversation history

## Requirements

- Backend server running on `http://localhost:8000`
- Python 3.8+
- Streamlit 1.28.0+

