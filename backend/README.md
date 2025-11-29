# Sicko Bot Backend API

FastAPI backend application for a chatbot with PDF ingestion and ChromaDB support.

## Features

1. **Azure OpenAI Integration** - Uses Azure OpenAI to formulate responses
2. **PDF Ingestion** - Upload and store PDF files in ChromaDB with embeddings
3. **File Management** - List, add, delete, and update PDF files
4. **Multi-turn Conversations** - Supports conversation history and context
5. **Citations** - Always provides source citations for answers

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment variables in `.env` file (in project root):
```
OPENAI_API_KEY=your_openai_api_key
# OR use Azure OpenAI:
AZURE_OPENAI_ENDPOINT=https://your-endpoint.openai.azure.com/
AZURE_OPENAI_API_KEY=your_azure_api_key
API_VERSION=2024-12-01-preview
```

3. Run the server:
```bash
python main.py
```

The server will start on `http://localhost:8000`

## API Endpoints

### Chat Endpoints

- `POST /api/chat/` - Send a chat message
  ```json
  {
    "message": "Your question",
    "conversation_id": "optional_id",
    "use_context": true
  }
  ```

- `GET /api/chat/conversations` - List all active conversations
- `DELETE /api/chat/conversation/{conversation_id}` - Clear a conversation

### File Management Endpoints

- `GET /api/files/` - List all PDF files in ChromaDB
- `POST /api/files/upload` - Upload a PDF file
- `DELETE /api/files/{filename}` - Delete a PDF file
- `PUT /api/files/{filename}` - Update a PDF file
- `GET /api/files/{filename}/info` - Get file information

### Health Check

- `GET /health` - Health check endpoint
- `GET /` - API information

## Testing

Run the test scripts to verify functionality:

```bash
# Test API endpoints
python test_endpoints.py

# Test configuration
python test_config.py

# Test PDF upload
python test_pdf_upload.py
```

## Project Structure

```
backend/
├── main.py                 # FastAPI application entry point
├── app/
│   ├── __init__.py
│   ├── config.py          # Configuration settings
│   ├── database.py         # ChromaDB setup
│   ├── embeddings.py      # Embedding generation
│   ├── llm.py             # LLM setup
│   ├── pdf_processor.py   # PDF processing
│   ├── vector_store.py    # Vector store operations
│   ├── chat.py            # Chat endpoints
│   └── files.py           # File management endpoints
├── requirements.txt
└── README.md
```

## Notes

- ChromaDB data is stored in `./chroma_db` directory
- Conversation history is stored in memory (use Redis/database for production)
- The API automatically uses Azure OpenAI if configured, otherwise falls back to OpenAI

