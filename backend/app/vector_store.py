"""
Vector store operations using ChromaDB
"""
from typing import List, Dict, Optional
from app.database import get_collection
from app.embeddings import get_embeddings
from app.pdf_processor import process_pdf
import hashlib

def add_pdf_to_store(pdf_content: bytes, filename: str) -> Dict:
    """Add PDF file to ChromaDB"""
    collection = get_collection()
    embeddings_model = get_embeddings()
    
    # Process PDF
    chunks = process_pdf(pdf_content, filename)
    
    if not chunks:
        raise Exception("No chunks created from PDF")
    
    # Generate embeddings
    texts = [chunk["text"] for chunk in chunks]
    embeddings = embeddings_model.embed_documents(texts)
    
    # Prepare data for ChromaDB
    ids = [chunk["id"] for chunk in chunks]
    metadatas = [
        {
            "filename": chunk["filename"],
            "source": chunk["source"],
            "chunk_index": chunk["chunk_index"],
            "total_chunks": chunk["total_chunks"]
        }
        for chunk in chunks
    ]
    
    # Add to collection
    collection.add(
        ids=ids,
        embeddings=embeddings,
        documents=texts,
        metadatas=metadatas
    )
    
    return {
        "filename": filename,
        "chunks_added": len(chunks),
        "status": "success"
    }

def search_similar_documents(query: str, n_results: int = 5) -> List[Dict]:
    """Search for similar documents in ChromaDB"""
    collection = get_collection()
    embeddings_model = get_embeddings()
    
    # Generate query embedding
    query_embedding = embeddings_model.embed_query(query)
    
    # Search in ChromaDB
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
        include=["documents", "metadatas", "distances"]
    )
    
    # Format results
    formatted_results = []
    if results["ids"] and len(results["ids"][0]) > 0:
        for i in range(len(results["ids"][0])):
            formatted_results.append({
                "id": results["ids"][0][i],
                "document": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "distance": results["distances"][0][i] if results["distances"] else None
            })
    
    return formatted_results

def list_all_files() -> List[Dict]:
    """List all unique files in ChromaDB"""
    collection = get_collection()
    
    # Get all data
    all_data = collection.get()
    
    # Extract unique filenames
    unique_files = {}
    if all_data["metadatas"]:
        for i, metadata in enumerate(all_data["metadatas"]):
            filename = metadata.get("filename", "unknown")
            if filename not in unique_files:
                unique_files[filename] = {
                    "filename": filename,
                    "chunk_count": 0,
                    "ids": []
                }
            unique_files[filename]["chunk_count"] += 1
            unique_files[filename]["ids"].append(all_data["ids"][i])
    
    return list(unique_files.values())

def delete_file(filename: str) -> Dict:
    """Delete all chunks associated with a filename"""
    collection = get_collection()
    
    # Get all data
    all_data = collection.get()
    
    # Find IDs to delete
    ids_to_delete = []
    if all_data["metadatas"]:
        for i, metadata in enumerate(all_data["metadatas"]):
            if metadata.get("filename") == filename:
                ids_to_delete.append(all_data["ids"][i])
    
    if not ids_to_delete:
        raise Exception(f"File '{filename}' not found in database")
    
    # Delete from collection
    collection.delete(ids=ids_to_delete)
    
    return {
        "filename": filename,
        "chunks_deleted": len(ids_to_delete),
        "status": "deleted"
    }

def update_file(filename: str, pdf_content: bytes) -> Dict:
    """Update a file by deleting old chunks and adding new ones"""
    # Delete existing file
    delete_file(filename)
    
    # Add new file
    return add_pdf_to_store(pdf_content, filename)

