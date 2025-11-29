"""
Streamlit Frontend for Sicko Bot - RAG Enabled Chatbot with PDF Management
"""
import streamlit as st
import requests
import json
from typing import List, Dict, Optional
import time

# Backend API URL
BACKEND_URL = "http://localhost:8000"

# Page configuration
st.set_page_config(
    page_title="Sicko Bot - RAG Chatbot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .stChatMessage {
        padding: 1rem;
    }
    .citation {
        background-color: #f0f2f6;
        padding: 0.5rem;
        border-radius: 0.5rem;
        margin-top: 0.5rem;
        font-size: 0.85rem;
    }
    .file-item {
        padding: 0.5rem;
        border: 1px solid #e0e0e0;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = f"conv_{int(time.time())}"
if "files" not in st.session_state:
    st.session_state.files = []

def check_backend_connection():
    """Check if backend is running"""
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=2)
        return response.status_code == 200
    except:
        return False

def get_files_list():
    """Get list of all PDF files from backend"""
    try:
        response = requests.get(f"{BACKEND_URL}/api/files/", timeout=5)
        if response.status_code == 200:
            files = response.json()
            # Ensure we return a list
            return files if isinstance(files, list) else []
        return []
    except requests.exceptions.ConnectionError:
        return []
    except Exception as e:
        # Don't show error in sidebar, just return empty list
        return []

def upload_pdf(file):
    """Upload PDF file to backend"""
    try:
        files = {'file': (file.name, file.getvalue(), 'application/pdf')}
        response = requests.post(f"{BACKEND_URL}/api/files/upload", files=files, timeout=60)
        if response.status_code == 200:
            return True, response.json()
        else:
            try:
                error_detail = response.json().get('detail', 'Upload failed')
            except:
                error_detail = response.text[:200] if response.text else 'Upload failed'
            return False, error_detail
    except requests.exceptions.Timeout:
        return False, "Upload timeout - file may be too large or server is slow"
    except requests.exceptions.ConnectionError:
        return False, "Cannot connect to backend server"
    except Exception as e:
        return False, f"Upload error: {str(e)}"

def delete_file(filename: str):
    """Delete PDF file from backend"""
    try:
        response = requests.delete(f"{BACKEND_URL}/api/files/{filename}", timeout=5)
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, response.json().get('detail', 'Delete failed')
    except Exception as e:
        return False, str(e)

def update_file(filename: str, file):
    """Update PDF file in backend"""
    try:
        files = {'file': (file.name, file.getvalue(), 'application/pdf')}
        response = requests.put(f"{BACKEND_URL}/api/files/{filename}", files=files, timeout=60)
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, response.json().get('detail', 'Update failed')
    except Exception as e:
        return False, str(e)

def send_chat_message(message: str, use_context: bool = True):
    """Send chat message to backend"""
    try:
        payload = {
            "message": message,
            "conversation_id": st.session_state.conversation_id,
            "use_context": use_context
        }
        response = requests.post(f"{BACKEND_URL}/api/chat/", json=payload, timeout=30)
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, response.json().get('detail', 'Chat failed')
    except Exception as e:
        return False, str(e)

def clear_conversation():
    """Clear conversation history"""
    try:
        response = requests.delete(f"{BACKEND_URL}/api/chat/conversation/{st.session_state.conversation_id}", timeout=5)
        st.session_state.messages = []
        st.session_state.conversation_id = f"conv_{int(time.time())}"
        return response.status_code in [200, 404]  # 404 means conversation doesn't exist, which is fine
    except:
        return True

# Main App
st.title("🤖 Sicko Bot - RAG Enabled Chatbot")
st.markdown("---")

# Check backend connection
if not check_backend_connection():
    st.error("⚠️ Backend server is not running. Please start the backend server first.")
    st.info("To start the backend: `cd backend && python main.py`")
    st.stop()

# Sidebar for file management
with st.sidebar:
    st.header("📁 PDF File Management")
    
    # File upload section
    st.subheader("Upload PDF")
    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type=['pdf'],
        help="Upload a PDF file to add it to the knowledge base"
    )
    
    if uploaded_file is not None:
        if st.button("📤 Upload PDF", use_container_width=True):
            with st.spinner("Uploading and processing PDF..."):
                success, result = upload_pdf(uploaded_file)
                if success:
                    filename = result.get('filename', 'File') if isinstance(result, dict) else 'File'
                    chunks = result.get('chunks_added', 0) if isinstance(result, dict) else 0
                    st.success(f"✅ {filename} uploaded successfully!")
                    st.info(f"📊 {chunks} chunks added to knowledge base")
                    # Force refresh file list - wait a bit for backend to process
                    time.sleep(1.5)  # Give backend time to process and index
                    # Clear the file uploader
                    st.session_state.uploaded_file = None
                    st.rerun()
                else:
                    error_msg = result if isinstance(result, str) else str(result)
                    st.error(f"❌ Upload failed: {error_msg}")
                    st.info("💡 Make sure the backend server is running and the PDF file is valid")
    
    st.markdown("---")
    
    # List of files - refresh on every render
    st.subheader("📋 Uploaded Files")
    # Always fetch fresh list from backend
    current_files = get_files_list()
    st.session_state.files = current_files
    
    # Show refresh button
    if st.button("🔄 Refresh List", key="refresh_files", use_container_width=True):
        st.session_state.files = get_files_list()
        st.rerun()
    
    if st.session_state.files:
        for file_info in st.session_state.files:
            filename = file_info.get('filename', 'Unknown')
            chunk_count = file_info.get('chunk_count', 0)
            
            with st.container():
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"**{filename}**")
                    st.caption(f"{chunk_count} chunks")
                
                with col2:
                    if st.button("🗑️", key=f"delete_{filename}", help="Delete file"):
                        with st.spinner("Deleting file..."):
                            success, result = delete_file(filename)
                            if success:
                                st.success(f"✅ {filename} deleted")
                                st.session_state.files = get_files_list()
                                time.sleep(0.5)
                                st.rerun()
                            else:
                                st.error(f"❌ Delete failed: {result}")
    else:
        st.info("No files uploaded yet")
    
    st.markdown("---")
    
    # Update file section
    st.subheader("🔄 Update File")
    if st.session_state.files:
        file_to_update = st.selectbox(
            "Select file to update",
            [f.get('filename') for f in st.session_state.files],
            key="update_select"
        )
        
        update_file_upload = st.file_uploader(
            "Upload new version",
            type=['pdf'],
            key="update_uploader",
            help="Upload a new version of the selected file"
        )
        
        if update_file_upload is not None and st.button("🔄 Update File", use_container_width=True):
            with st.spinner("Updating file..."):
                success, result = update_file(file_to_update, update_file_upload)
                if success:
                    st.success(f"✅ {file_to_update} updated successfully!")
                    st.info(f"📊 {result.get('chunks_added', 0)} chunks added")
                    st.session_state.files = get_files_list()
                    time.sleep(0.5)
                    st.rerun()
                else:
                    st.error(f"❌ Update failed: {result}")
    
    st.markdown("---")
    
    # Conversation controls
    st.subheader("💬 Conversation")
    if st.button("🗑️ Clear Conversation", use_container_width=True):
        clear_conversation()
        st.success("Conversation cleared!")
        st.rerun()
    
    st.caption(f"Conversation ID: {st.session_state.conversation_id[:20]}...")

# Main chat interface
st.header("💬 Chat with Sicko Bot")

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        
        # Display citations if available
        if "citations" in message and message["citations"]:
            with st.expander("📚 Citations", expanded=False):
                for i, citation in enumerate(message["citations"], 1):
                    # Format relevance score properly
                    relevance_score = citation.get('relevance_score')
                    if relevance_score is not None:
                        relevance_str = f"{relevance_score:.2f}"
                    else:
                        relevance_str = "N/A"
                    
                    st.markdown(f"""
                    <div class="citation">
                        <strong>Source {i}:</strong> {citation.get('source', 'Unknown')}<br>
                        <em>Relevance: {relevance_str}</em>
                    </div>
                    """, unsafe_allow_html=True)
                    st.caption(citation.get('content', '')[:200] + "...")

# Chat input
if prompt := st.chat_input("Ask me anything about your documents..."):
    # Add user message to chat
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Get response from backend
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            # Always check current file list to determine if context should be used
            current_files = get_files_list()
            use_context = len(current_files) > 0  # Use context if files are available
            if use_context:
                st.info(f"🔍 Searching through {len(current_files)} document(s)...")
            success, response = send_chat_message(prompt, use_context=use_context)
            
            if success:
                response_text = response.get('response', '')
                citations = response.get('citations', [])
                
                # Display response
                st.markdown(response_text)
                
                # Display citations
                if citations:
                    st.markdown("### 📚 Sources")
                    for i, citation in enumerate(citations, 1):
                        # Format relevance score properly
                        relevance_score = citation.get('relevance_score')
                        if relevance_score is not None:
                            relevance_str = f"{relevance_score:.2f}"
                        else:
                            relevance_str = "N/A"
                        
                        st.markdown(f"""
                        <div class="citation">
                            <strong>Source {i}:</strong> {citation.get('source', 'Unknown')}<br>
                            <em>Relevance Score: {relevance_str}</em>
                        </div>
                        """, unsafe_allow_html=True)
                        with st.expander(f"View content from {citation.get('source', 'Unknown')}"):
                            st.text(citation.get('content', ''))
                
                # Add assistant message to chat
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response_text,
                    "citations": citations
                })
            else:
                error_msg = f"❌ Error: {response}"
                st.error(error_msg)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_msg
                })

# Footer
st.markdown("---")
st.caption("💡 Tip: Upload PDF files to enable RAG (Retrieval Augmented Generation) for context-aware responses with citations.")

