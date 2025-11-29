# Sicko Bot - RAG Enabled Chatbot

A full-stack RAG (Retrieval Augmented Generation) chatbot application with PDF document ingestion, built with FastAPI backend and Streamlit frontend.

## 🚀 Features

### Backend (FastAPI)
- **RAG-Enabled Chatbot** - Uses OpenAI/Azure OpenAI for intelligent responses
- **PDF Document Ingestion** - Upload, process, and store PDF files in ChromaDB
- **Vector Search** - Semantic search through document embeddings
- **File Management** - List, add, delete, and update PDF files
- **Multi-turn Conversations** - Maintains conversation context
- **Citations** - Always provides source citations for answers

### Frontend (Streamlit)
- **Interactive Chat Interface** - Clean, user-friendly chat UI
- **PDF Upload & Management** - Easy file upload and management
- **Citation Display** - Visual citation display with source information
- **Real-time Updates** - Automatic file list refresh
- **Conversation History** - View and manage chat history

## 📋 Prerequisites

- Python 3.8 or higher
- OpenAI API key or Azure OpenAI credentials
- Git

## 🛠️ Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd sicko-bot
```

### 2. Install Backend Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 3. Install Frontend Dependencies

```bash
cd ../frontend
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```env
# OpenAI Configuration (choose one)
OPENAI_API_KEY=your_openai_api_key_here

# OR Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT=https://your-endpoint.openai.azure.com/
AZURE_OPENAI_API_KEY=your_azure_api_key_here
API_VERSION=2024-12-01-preview

# Optional Configuration
CHROMA_DB_PATH=./chroma_db
COLLECTION_NAME=sicko_bot_documents
EMBEDDING_MODEL=text-embedding-ada-002
CHAT_MODEL=gpt-4
```

## 🚀 Running the Application

### Start Backend Server

Open a terminal and run:

```bash
cd backend
python main.py
```

The backend will start on `http://localhost:8000`

### Start Frontend Application

Open a **new terminal** and run:

```bash
cd frontend
streamlit run app.py
```

The frontend will open automatically in your browser at `http://localhost:8501`

### Quick Start (Windows)

```bash
# Terminal 1 - Backend
cd backend && python main.py

# Terminal 2 - Frontend
cd frontend && streamlit run app.py
```

## 📖 Usage

### 1. Upload PDF Documents

1. Open the frontend in your browser
2. Use the sidebar to upload PDF files
3. Wait for processing confirmation
4. Files will appear in the "Uploaded Files" section

### 2. Chat with Documents

1. Type your question in the chat input
2. The bot will search through uploaded documents
3. Responses include citations from source documents
4. Click on citations to view source content

### 3. Manage Files

- **Delete**: Click the 🗑️ button next to a file
- **Update**: Select a file and upload a new version
- **Refresh**: Click "🔄 Refresh List" to update the file list

### 4. Clear Conversation

Click "🗑️ Clear Conversation" in the sidebar to reset chat history

## 🏗️ Project Structure

```
sicko-bot/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── chat.py              # Chat endpoints
│   │   ├── config.py            # Configuration
│   │   ├── database.py           # ChromaDB setup
│   │   ├── embeddings.py         # Embedding generation
│   │   ├── files.py             # File management endpoints
│   │   ├── llm.py               # LLM setup
│   │   ├── pdf_processor.py     # PDF processing
│   │   └── vector_store.py      # Vector store operations
│   ├── main.py                  # FastAPI application
│   ├── requirements.txt         # Backend dependencies
│   └── README.md                # Backend documentation
├── frontend/
│   ├── app.py                   # Streamlit application
│   ├── requirements.txt         # Frontend dependencies
│   ├── README.md                # Frontend documentation
│   └── start_frontend.bat       # Windows startup script
├── sample_pdfs/                 # Sample PDF files
├── .env                         # Environment variables (not in git)
├── requirements.txt             # Root dependencies
└── README.md                    # This file
```

## 🔌 API Endpoints

### Chat Endpoints

- `POST /api/chat/` - Send a chat message
- `GET /api/chat/conversations` - List active conversations
- `DELETE /api/chat/conversation/{id}` - Clear a conversation

### File Management Endpoints

- `GET /api/files/` - List all PDF files
- `POST /api/files/upload` - Upload a PDF file
- `DELETE /api/files/{filename}` - Delete a PDF file
- `PUT /api/files/{filename}` - Update a PDF file
- `GET /api/files/{filename}/info` - Get file information

### Health Check

- `GET /health` - Health check endpoint
- `GET /` - API information

## 🧪 Testing

### Test Backend

```bash
cd backend
python -c "import requests; r = requests.get('http://localhost:8000/health'); print(r.json())"
```

### Test Frontend

1. Start both backend and frontend
2. Upload a PDF file
3. Ask a question about the document
4. Verify citations appear

## 🐛 Troubleshooting

### Backend Not Starting

- Check if port 8000 is available
- Verify `.env` file exists and has valid API keys
- Check Python version (3.8+)

### Frontend Can't Connect to Backend

- Ensure backend is running on `http://localhost:8000`
- Check backend health endpoint: `http://localhost:8000/health`

### PDF Upload Fails

- Verify PDF file is valid
- Check file size (recommended < 50MB)
- Ensure backend server is running
- Check backend logs for errors

### Chat Not Using Context

- Make sure PDF files are uploaded first
- Check "Uploaded Files" section shows files
- Verify `use_context: true` in API calls

### Citations Not Showing

- Ensure files are uploaded and processed
- Check that responses include citations from backend
- Verify relevance scores are calculated

## 📝 Notes

- ChromaDB data is stored in `backend/chroma_db/` directory
- Conversation history is stored in memory (restart clears it)
- For production, consider using Redis or a database for conversation storage
- Large PDF files may take time to process

## 🔒 Security

- Never commit `.env` file to git
- Keep API keys secure
- Use environment variables for sensitive data
- Consider rate limiting for production

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is open source and available under the MIT License.

## 👤 Author

**Hrithiksinha1**

## 🙏 Acknowledgments

- OpenAI for the API
- ChromaDB for vector storage
- FastAPI and Streamlit communities

---

For detailed backend documentation, see [backend/README.md](backend/README.md)  
For detailed frontend documentation, see [frontend/README.md](frontend/README.md)

