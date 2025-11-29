"""
Chat endpoints with multi-turn conversation support
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from app.llm import get_llm
from app.vector_store import search_similar_documents
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate

chat_router = APIRouter()

# Store conversation histories (in production, use Redis or database)
conversation_memories: Dict[str, ConversationBufferMemory] = {}

class ChatMessage(BaseModel):
    message: str
    conversation_id: Optional[str] = "default"
    use_context: bool = True

class ChatResponse(BaseModel):
    response: str
    citations: List[Dict[str, Any]]
    conversation_id: str

def get_conversation_memory(conversation_id: str) -> ConversationBufferMemory:
    """Get or create conversation memory"""
    if conversation_id not in conversation_memories:
        conversation_memories[conversation_id] = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            output_key="answer"
        )
    return conversation_memories[conversation_id]

def format_citations(search_results: List[Dict]) -> List[Dict]:
    """Format search results as citations"""
    citations = []
    seen_sources = set()
    
    for result in search_results:
        source = result.get("metadata", {}).get("filename", "Unknown")
        if source not in seen_sources:
            citations.append({
                "source": source,
                "content": result.get("document", "")[:200] + "...",  # Truncate for display
                "relevance_score": 1 - result.get("distance", 1.0) if result.get("distance") else None
            })
            seen_sources.add(source)
    
    return citations

@chat_router.post("/", response_model=ChatResponse)
async def chat(message: ChatMessage):
    """
    Chat endpoint with multi-turn conversation support and citations
    """
    try:
        llm = get_llm()
        memory = get_conversation_memory(message.conversation_id)
        
        # If use_context is True, search for relevant documents
        context = ""
        citations = []
        
        if message.use_context:
            # Search for relevant documents
            search_results = search_similar_documents(message.message, n_results=5)
            
            if search_results:
                # Build context from search results
                context_parts = []
                for i, result in enumerate(search_results, 1):
                    doc_text = result.get("document", "")
                    source = result.get("metadata", {}).get("filename", "Unknown")
                    context_parts.append(f"[Source {i}: {source}]\n{doc_text}\n")
                
                context = "\n\n".join(context_parts)
                citations = format_citations(search_results)
        
        # Create prompt template
        if context:
            prompt_template = """You are a helpful AI assistant. Use the following context to answer the question. 
Always cite your sources when using information from the context.

Context:
{context}

Chat History:
{chat_history}

Question: {question}

Answer:"""
        else:
            prompt_template = """You are a helpful AI assistant. Answer the question based on your knowledge.

Chat History:
{chat_history}

Question: {question}

Answer:"""
        
        prompt = PromptTemplate(
            template=prompt_template,
            input_variables=["context", "chat_history", "question"]
        )
        
        # Get chat history
        chat_history = memory.chat_memory.messages if hasattr(memory, 'chat_memory') else []
        chat_history_str = "\n".join([
            f"{'Human' if i % 2 == 0 else 'Assistant'}: {msg.content if hasattr(msg, 'content') else str(msg)}"
            for i, msg in enumerate(chat_history[-6:])  # Last 3 exchanges
        ])
        
        # Generate response
        if context:
            full_prompt = prompt.format(
                context=context,
                chat_history=chat_history_str,
                question=message.message
            )
        else:
            full_prompt = prompt.format(
                context="",
                chat_history=chat_history_str,
                question=message.message
            )
        
        response = llm.invoke(full_prompt)
        response_text = response.content if hasattr(response, 'content') else str(response)
        
        # Save to memory
        memory.chat_memory.add_user_message(message.message)
        memory.chat_memory.add_ai_message(response_text)
        
        return ChatResponse(
            response=response_text,
            citations=citations,
            conversation_id=message.conversation_id
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing chat: {str(e)}")

@chat_router.delete("/conversation/{conversation_id}")
async def clear_conversation(conversation_id: str):
    """Clear conversation history"""
    if conversation_id in conversation_memories:
        del conversation_memories[conversation_id]
        return {"status": "cleared", "conversation_id": conversation_id}
    else:
        raise HTTPException(status_code=404, detail="Conversation not found")

@chat_router.get("/conversations")
async def list_conversations():
    """List all active conversations"""
    return {
        "conversations": list(conversation_memories.keys()),
        "count": len(conversation_memories)
    }

