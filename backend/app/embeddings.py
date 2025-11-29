"""
Embedding generation using OpenAI/Azure OpenAI
"""
from langchain_openai import AzureOpenAIEmbeddings, OpenAIEmbeddings
from app.config import USE_AZURE, AZURE_OPENAI_ENDPOINT, OPENAI_API_KEY_TO_USE, API_VERSION, EMBEDDING_MODEL

def get_embeddings():
    """Get embeddings model"""
    if USE_AZURE:
        return AzureOpenAIEmbeddings(
            azure_endpoint=AZURE_OPENAI_ENDPOINT,
            api_key=OPENAI_API_KEY_TO_USE,
            api_version=API_VERSION,
            model=EMBEDDING_MODEL
        )
    else:
        return OpenAIEmbeddings(
            openai_api_key=OPENAI_API_KEY_TO_USE,
            model=EMBEDDING_MODEL
        )

