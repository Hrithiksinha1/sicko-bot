#!/usr/bin/env python
# coding: utf-8

# In[1]:


from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    Docx2txtLoader,
    CSVLoader,
    UnstructuredMarkdownLoader
)
from pathlib import Path
import os
import shutil


# In[2]:


import os
from dotenv import load_dotenv
load_dotenv()
openai_api_key =  os.getenv("OPENAI_API_KEY")


# In[3]:
Nokia CMDLSTML. 

from langchain_experimental.text_splitter import SemanticChunker
from langchain_openai import OpenAIEmbeddings
from datetime import datetime


# So now we are uploading the Documnets and storing it in a forlder Uploaded Documents.

# In[4]:


def create_upload_directory(upload_dir="uploaded_documents"):
    """
    Create the upload directory if it doesn't exist
    
    Args:
        upload_dir (str): Directory where uploaded documents will be stored
    
    Returns:
        str: Path to the created directory
    """
    Path(upload_dir).mkdir(parents=True, exist_ok=True)
    print(f"Upload directory ready: {upload_dir}")
    return upload_dir


# In[5]:


def upload_document(file_path, upload_dir="uploaded_documents"):
    """
    Upload a document to the upload directory
    
    Args:
        file_path (str): Path to the file to upload
        upload_dir (str): Directory where the file will be uploaded
        
    Returns:
        str: Path to the uploaded file
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    # Create directory if it doesn't exist
    create_upload_directory(upload_dir)
    
    file_name = os.path.basename(file_path)
    destination = os.path.join(upload_dir, file_name)
    
    # Copy file to upload directory
    shutil.copy2(file_path, destination)
    
    print(f"Document uploaded successfully: {destination}")
    return destination


# In[6]:


def load_document(file_path):
    """
    Load a document using the appropriate LangChain loader
    
    Args:
        file_path (str): Path to the document
        
    Returns:
        list: List of Document objects
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    file_extension = Path(file_path).suffix.lower()
    
    loaders = {
        '.pdf': PyPDFLoader,
        '.txt': TextLoader,
        '.docx': Docx2txtLoader,
        '.csv': CSVLoader,
        '.md': UnstructuredMarkdownLoader
    }
    
    loader_class = loaders.get(file_extension)
    
    if not loader_class:
        raise ValueError(f"Unsupported file type: {file_extension}")
    
    print(f"Loading document with {loader_class.__name__}...")
    loader = loader_class(file_path)
    documents = loader.load()
    
    print(f"Loaded {len(documents)} document(s)")
    return documents


# In[7]:


import pypdf

# Prompt user for file path
file_path = input("Enter the path to the document you want to upload: ")

uploaded_path = upload_document(
    file_path=file_path,
)

docs = load_document(uploaded_path)


# In[8]:


# from langchain_text_splitters import RecursiveCharacterTextSplitter

# def split_documents(documents, chunk_size=1000, chunk_overlap=200):
#     """
#     Split documents into smaller chunks using fixed-size chunking
    
#     Args:
#         documents (list): List of Document objects
#         chunk_size (int): Size of each chunk
#         chunk_overlap (int): Overlap between chunks
        
#     Returns:
#         list: List of split Document objects with preserved metadata
#     """
#     text_splitter = RecursiveCharacterTextSplitter(
#         chunk_size=chunk_size,
#         chunk_overlap=chunk_overlap,
#         length_function=len,
#         add_start_index=True  # Adds character index to metadata
#     )
    
#     split_docs = text_splitter.split_documents(documents)
    
#     # Add additional metadata to each chunk
#     for i, doc in enumerate(split_docs):
#         doc.metadata['chunk_id'] = i
#         doc.metadata['chunk_size'] = len(doc.page_content)
#         doc.metadata['chunking_method'] = 'fixed_size'
#         doc.metadata['timestamp'] = datetime.now().isoformat()
    
#     print(f"Split into {len(split_docs)} chunks using fixed-size chunking")
#     return split_docs


# In[9]:


def semantic_split_documents(documents, embeddings_model=None, breakpoint_threshold_type="percentile"):
    """
    Split documents using semantic chunking (groups text by meaning)
    
    Args:
        documents (list): List of Document objects
        embeddings_model: Embeddings model to use (default: OpenAIEmbeddings)
        breakpoint_threshold_type (str): "percentile", "standard_deviation", or "interquartile"
        
    Returns:
        list: List of semantically split Document objects with metadata
    """
    if embeddings_model is None:
        # You can replace this with other embedding models
        embeddings_model = OpenAIEmbeddings()
    
    text_splitter = SemanticChunker(
        embeddings_model,
        breakpoint_threshold_type=breakpoint_threshold_type
    )
    
    split_docs = text_splitter.split_documents(documents)
    
    # Add metadata to each chunk
    for i, doc in enumerate(split_docs):
        doc.metadata['chunk_id'] = i
        doc.metadata['chunk_size'] = len(doc.page_content)
        doc.metadata['chunking_method'] = 'semantic'
        doc.metadata['breakpoint_type'] = breakpoint_threshold_type
        doc.metadata['timestamp'] = datetime.now().isoformat()
        doc.metadata['page'] = doc.metadata.get('page', 'unknown')
    
    print(f"Split into {len(split_docs)} chunks using semantic chunking")
    return split_docs


# In[10]:


def get_chunk_metadata(chunk):
    """
    Display all metadata for a specific chunk
    
    Args:
        chunk: A Document object
        
    Returns:
        dict: Metadata dictionary
    """
    print("\n--- Chunk Metadata ---")
    for key, value in chunk.metadata.items():
        print(f"{key}: {value}")
    
    return chunk.metadata


# In[11]:


from langchain_openai import OpenAIEmbeddings

# Load document

# Semantic chunking (groups by meaning)
chunks = semantic_split_documents(docs, embeddings_model=OpenAIEmbeddings())

# Check metadata
print(chunks[0].metadata)
# Output includes: chunk_id, chunk_size, chunking_method, breakpoint_type, timestamp


# In[13]:


import chromadb
from chromadb.utils import embedding_functions

def store_embeddings_in_chroma(chunks, embeddings_model=None, persist_directory="chroma"):
    """
    Generates embeddings for the document chunks and stores them in Chroma DB.
    
    Args:
        chunks (list): List of Document objects (chunks of text).
        embeddings_model: Embeddings model to use (default: OpenAIEmbeddings).
        persist_directory (str): Directory to persist the Chroma DB.
        
    Returns:
        chromadb.Client: Chroma DB client.
    """
    if embeddings_model is None:
        embeddings_model = OpenAIEmbeddings()

    # Extract text from document chunks
    texts = [chunk.page_content for chunk in chunks]

    # Generate embeddings
    embeddings = embeddings_model.embed_documents(texts)

    # Create Chroma client
    chroma_client = chromadb.PersistentClient(path=persist_directory)

    # Create a collection in Chroma
    collection = chroma_client.get_or_create_collection(
        name="my_collection",  # You can change the collection name
        embedding_function=embedding_functions.OpenAIEmbeddingFunction(
            model_name="text-embedding-ada-002"
        )
    )

    # Add embeddings and text to Chroma
    collection.add(
        embeddings=embeddings,
        documents=texts,
        ids=[str(i) for i in range(len(chunks))]  # Unique IDs for each chunk
    )

    print(f"Stored {len(chunks)} embeddings in Chroma DB at {persist_directory}")
    return chroma_client


# In[14]:


import chromadb
from chromadb.utils import embedding_functions

# Call the function to store embeddings in Chroma
chroma_client = store_embeddings_in_chroma(chunks)



# In[15]:


import sqlite3
import json
import uuid

def save_metadata_to_sqlite(
    documents,
    db_path="metadata.db",
    table_name="documents_metadata",
    preview_chars=300
):
    """
    Save metadata from LangChain Document objects into SQLite.
    Stores: id, page_number, chunk_id, chunk_size, chunking_method, timestamp, preview, full metadata.
    """
    
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # Create table with page number column
    cur.execute(f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id TEXT PRIMARY KEY,
            page_number INTEGER,
            chunk_id INTEGER,
            chunk_size INTEGER,
            chunking_method TEXT,
            timestamp TEXT,
            text_preview TEXT,
            metadata_json TEXT
        );
    """)

    ids = []

    for doc in documents:
        # Stable ID
        doc_id = doc.metadata.get("id") or str(uuid.uuid4())
        doc.metadata["id"] = doc_id
        ids.append(doc_id)

        # Extract fields
        page_number = doc.metadata.get("page", None)           # <-- NEW  
        chunk_id = doc.metadata.get("chunk_id")
        chunk_size = doc.metadata.get("chunk_size", len(doc.page_content))
        chunking_method = doc.metadata.get("chunking_method")
        timestamp = doc.metadata.get("timestamp")
        text_preview = doc.page_content[:preview_chars]

        # Save full metadata JSON
        metadata_json = json.dumps(doc.metadata, ensure_ascii=False)

        cur.execute(
            f"""
            INSERT OR REPLACE INTO {table_name} 
            (id, page_number, chunk_id, chunk_size, chunking_method, timestamp, text_preview, metadata_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                doc_id,
                page_number,       # <-- NEW
                chunk_id,
                chunk_size,
                chunking_method,
                timestamp,
                text_preview,
                metadata_json
            )
        )

    conn.commit()
    conn.close()

    print(f"Saved metadata for {len(documents)} chunks → {db_path}:{table_name}")
    return ids


# In[16]:


# Save metadata to SQLite
ids = save_metadata_to_sqlite(
    documents=chunks,
    db_path="uploaded_documents/metadata.db",
    table_name="documents_metadata"
)


# In[17]:


# ... previous code ...

import sqlite3
import chromadb
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings

def similarity_search_with_metadata(query, chroma_path="chroma", sqlite_path="uploaded_documents/metadata.db", table_name="documents_metadata", top_k=2, embeddings_model=None):
    """
    Perform a similarity search in ChromaDB and augment results with metadata from SQLite.

    Args:
        query (str): The search query.
        chroma_path (str): Path to the persisted Chroma database.
        sqlite_path (str): Path to the SQLite database containing document metadata.
        table_name (str): Name of the table in the SQLite database.
        top_k (int): Number of results to return.
        embeddings_model: Embeddings model to use for similarity search (default: OpenAIEmbeddings).

    Returns:
        list: A list of Document objects, each containing the chunk content and metadata from both Chroma and SQLite.
    """

    if embeddings_model is None:
        embeddings_model = OpenAIEmbeddings()

    # Initialize Chroma client
    chroma_client = chromadb.PersistentClient(path=chroma_path)
    collection = chroma_client.get_or_create_collection(
        name="my_collection",  # Ensure this matches the collection name used during storage
        embedding_function=chromadb.utils.embedding_functions.OpenAIEmbeddingFunction(
            model_name="text-embedding-ada-002"
        )
    )

    embedding = embeddings_model.embed_query(query)

    # Perform similarity search in Chroma
    results = collection.query(
        query_embeddings=[embedding],
        n_results=top_k,
        include=["documents"],
    )

    # Extract relevant information from Chroma results
    ids = results["ids"][0]  # Chunk IDs from Chroma
    documents = results["documents"][0]  # Chunk contents

    # Fetch metadata from SQLite
    conn = sqlite3.connect(sqlite_path)
    cursor = conn.cursor()

    # Prepare the IN clause for the SQL query
    placeholders = ', '.join('?' for _ in ids)
    sql_query = f"SELECT * FROM {table_name} WHERE id IN ({placeholders})"

    cursor.execute(sql_query, ids)
    metadata_rows = cursor.fetchall()
    column_names = [description[0] for description in cursor.description]

    conn.close()

    # Create a dictionary mapping ID to metadata for easy lookup
    metadata_dict = {row[0]: dict(zip(column_names, row)) for row in metadata_rows}

    # Combine chunk content with metadata
    combined_results = []
    for i, doc_id in enumerate(ids):
        metadata = metadata_dict.get(doc_id)
        if metadata:
            combined_metadata = metadata  # Use all metadata from SQLite
            combined_results.append(
                Document(
                    page_content=documents[i],
                    metadata=combined_metadata
                )
            )
        else:
            print(f"Warning: Metadata not found for chunk ID {doc_id}")
            # Still create a Document, but with limited info
            combined_results.append(
                Document(page_content=documents[i], metadata={"id": doc_id})
            )

    return combined_results

# Example usage:
results = similarity_search_with_metadata("What is keeper?", top_k=3)

for result in results:
    print(f"Content: {result.page_content}\nMetadata: {result.metadata}\n---")


# In[18]:


# ... previous imports ...

from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI


# ... previous code ...

def generate_answer(system_prompt, chunks, question, history=None, model_name="gpt-3.5-turbo", max_history=5):
    system_prompt = """You are a helpful assistant that answers questions about the document. You must answer strictly based on the context provided in the documents. If the answer is not contained within the text below, say "I don't know". """

    # Initialize chat model
    llm = ChatOpenAI(model_name=model_name, temperature=0.1)

    # -----------------------------
    # ✅ NEW MEMORY IMPLEMENTATION
    # -----------------------------
    # Use InMemoryChatMessageHistory to store conversation state
    chat_memory = InMemoryChatMessageHistory()

    # Seed existing history if provided (list of HumanMessage/AIMessage)
    if history:
        for msg in history:
            chat_memory.add_message(msg)

    # Load existing messages for prompt
    chat_history_messages = chat_memory.messages

    # -----------------------------
    # Prepare RAG context
    # -----------------------------
    context = "\n".join([f"{chunk.page_content}" for chunk in chunks])

    # Build prompt
    prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt + "\n\nContext:\n{context}"),
    MessagesPlaceholder(variable_name="chat_history"),
    ("user", "{question}")
    ])
    # Build LCEL chain
    chain = (
        {"context": (lambda x: context), "question": (lambda x: question), "chat_history": (lambda x: chat_history_messages)}
        | prompt
        | llm.bind(stop=["\nUser"])
    )

    # Run Model
    response = chain.invoke({
        "question": question,
        "chat_history": chat_history_messages
    })

    # ------------------------------------
    # Save new interaction to chat memory
    # ------------------------------------
    chat_memory.add_user_message(question)
    chat_memory.add_ai_message(response.content)

    # ------------------------------------
    # Trim history to last N turns
    # Each turn = 2 messages (Human + AI)
    # ------------------------------------
    trimmed = chat_memory.messages[-(max_history * 2):]

    return response.content, trimmed


# In[21]:


# Debugging cell: Check retrieval and LLM context
question = "Can you let me know the first question I asked?"
results = similarity_search_with_metadata(question, top_k=3)

print("--- Retrieved Chunks ---")
for i, result in enumerate(results):
    print(f"Chunk {i+1} Content:\n{result.page_content}\nMetadata: {result.metadata}\n---")

# Pass retrieved chunks to LLM
answer, history = generate_answer(
    system_prompt="You are a helpful assistant that answers questions about the document. You must answer strictly based on the context provided in the documents. If the answer is not contained within the text below, say 'I don't know'. ",
    chunks=results,
    question=question
)

print(f"Question: {question}\nAnswer: {answer}")# Removed duplicate print statement

