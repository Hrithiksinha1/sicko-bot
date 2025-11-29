"""
FastAPI Backend for Chatbot with PDF Ingestion and ChromaDB
"""
from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
from dotenv import load_dotenv
import uvicorn

from app.chat import chat_router
from app.files import files_router
from app.database import init_db

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Sicko Bot API",
    description="Chatbot API with PDF ingestion and ChromaDB support",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat_router, prefix="/api/chat", tags=["Chat"])
app.include_router(files_router, prefix="/api/files", tags=["Files"])

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    init_db()
    print("Database initialized")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Sicko Bot API",
        "version": "1.0.0",
        "endpoints": {
            "chat": "/api/chat",
            "files": "/api/files"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

