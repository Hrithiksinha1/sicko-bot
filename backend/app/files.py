"""
File management endpoints for PDF files in ChromaDB
"""
from fastapi import APIRouter, File, UploadFile, HTTPException
from typing import List, Dict
from app.vector_store import add_pdf_to_store, list_all_files, delete_file, update_file

files_router = APIRouter()

@files_router.get("/", response_model=List[Dict])
async def list_files():
    """
    List all PDF files stored in ChromaDB
    """
    try:
        files = list_all_files()
        return files
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing files: {str(e)}")

@files_router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Upload and ingest a PDF file into ChromaDB
    """
    try:
        # Validate file type
        if not file.filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")
        
        # Read file content
        pdf_content = await file.read()
        
        if len(pdf_content) == 0:
            raise HTTPException(status_code=400, detail="File is empty")
        
        # Add to vector store
        result = add_pdf_to_store(pdf_content, file.filename)
        
        return {
            "message": "File uploaded and processed successfully",
            **result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")

@files_router.delete("/{filename}")
async def remove_file(filename: str):
    """
    Delete a PDF file from ChromaDB
    """
    try:
        result = delete_file(filename)
        return {
            "message": "File deleted successfully",
            **result
        }
    except Exception as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail=str(e))
        raise HTTPException(status_code=500, detail=f"Error deleting file: {str(e)}")

@files_router.put("/{filename}")
async def update_pdf_file(filename: str, file: UploadFile = File(...)):
    """
    Update a PDF file in ChromaDB (deletes old and adds new)
    """
    try:
        # Validate file type
        if not file.filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")
        
        # Read file content
        pdf_content = await file.read()
        
        if len(pdf_content) == 0:
            raise HTTPException(status_code=400, detail="File is empty")
        
        # Update file
        result = update_file(filename, pdf_content)
        
        return {
            "message": "File updated successfully",
            **result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail=str(e))
        raise HTTPException(status_code=500, detail=f"Error updating file: {str(e)}")

@files_router.get("/{filename}/info")
async def get_file_info(filename: str):
    """
    Get information about a specific file
    """
    try:
        files = list_all_files()
        file_info = next((f for f in files if f["filename"] == filename), None)
        
        if not file_info:
            raise HTTPException(status_code=404, detail=f"File '{filename}' not found")
        
        return file_info
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting file info: {str(e)}")

