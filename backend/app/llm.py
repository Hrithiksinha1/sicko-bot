"""
LLM setup for Azure OpenAI or OpenAI
"""
from langchain_openai import AzureChatOpenAI, ChatOpenAI
from app.config import (
    USE_AZURE, 
    AZURE_OPENAI_ENDPOINT, 
    OPENAI_API_KEY_TO_USE, 
    API_VERSION, 
    CHAT_MODEL,
    AZURE_CHAT_MODEL
)

def get_llm(temperature=0.7):
    """Get LLM instance"""
    if USE_AZURE:
        return AzureChatOpenAI(
            azure_endpoint=AZURE_OPENAI_ENDPOINT,
            api_key=OPENAI_API_KEY_TO_USE,
            api_version=API_VERSION,
            azure_deployment=AZURE_CHAT_MODEL,
            temperature=temperature
        )
    else:
        return ChatOpenAI(
            openai_api_key=OPENAI_API_KEY_TO_USE,
            model_name=CHAT_MODEL,
            temperature=temperature
        )

