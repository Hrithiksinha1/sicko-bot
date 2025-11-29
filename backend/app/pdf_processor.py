"""
PDF processing and chunking
"""
from pypdf import PdfReader
from typing import List, Dict
import uuid
from io import BytesIO
from langchain.text_splitter import RecursiveCharacterTextSplitter

def extract_text_from_pdf(pdf_content: bytes) -> str:
    """Extract text from PDF content"""
    try:
        # Convert bytes to BytesIO for PdfReader
        pdf_file = BytesIO(pdf_content)
        pdf_reader = PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        raise Exception(f"Error extracting text from PDF: {str(e)}")

def chunk_text(text: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> List[Dict]:
    """Split text into chunks with metadata"""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
    )
    
    chunks = text_splitter.split_text(text)
    
    # Create chunks with unique IDs
    chunk_docs = []
    for i, chunk in enumerate(chunks):
        chunk_docs.append({
            "id": str(uuid.uuid4()),
            "text": chunk,
            "chunk_index": i,
            "total_chunks": len(chunks)
        })
    
    return chunk_docs

def process_pdf(pdf_content: bytes, filename: str) -> List[Dict]:
    """Process PDF file and return chunks"""
    # Extract text
    text = extract_text_from_pdf(pdf_content)
    
    if not text.strip():
        raise Exception("No text could be extracted from the PDF")
    
    # Chunk text
    chunks = chunk_text(text)
    
    # Add filename metadata to each chunk
    for chunk in chunks:
        chunk["filename"] = filename
        chunk["source"] = filename
    
    return chunks

