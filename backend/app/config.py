"""
Configuration settings
"""
import os
from dotenv import load_dotenv
from pathlib import Path

# Load .env from parent directory (project root)
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)
# Also try loading from current directory
load_dotenv()

# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", "").strip()
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY", "").strip()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
API_VERSION = os.getenv("API_VERSION", "2024-12-01-preview")

# Use Azure OpenAI if available, otherwise fall back to OpenAI
USE_AZURE = bool(AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_API_KEY)
OPENAI_API_KEY_TO_USE = AZURE_OPENAI_API_KEY if USE_AZURE else OPENAI_API_KEY

# ChromaDB Configuration
CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", "./chroma_db")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "sicko_bot_documents")

# Embedding Model
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-ada-002")

# Chat Model
CHAT_MODEL = os.getenv("CHAT_MODEL", "gpt-4")

# Azure OpenAI Chat Model (if using Azure)
AZURE_CHAT_MODEL = os.getenv("AZURE_CHAT_MODEL", "gpt-4")

print(f"Configuration loaded - Using {'Azure OpenAI' if USE_AZURE else 'OpenAI'}")

