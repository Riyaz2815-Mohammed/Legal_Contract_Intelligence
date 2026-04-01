import os
from langchain.chat_models import init_chat_model
from langchain_core.language_models.chat_models import BaseChatModel
from vector_pipeline.config.settings import LLM_PROVIDER, LLM_MODEL, LLM_API_KEY, LLM_TEMPERATURE

def get_llm_instance() -> BaseChatModel:
    """
    Factory to return a generic LangChain chat model.
    Initializes dynamically based on abstract .env settings.
    """
    if not LLM_API_KEY:
        raise ValueError("LLM_API_KEY is not set in the environment.")
    
    provider = LLM_PROVIDER.strip().lower()
    
    # Map friendly provider names to langchain provider names
    # e.g., 'mistral' -> 'mistralai'
    if provider == "mistral":
        lc_provider = "mistralai"
    elif provider == "google" or provider == "gemini":
        lc_provider = "google_genai"
    else:
        lc_provider = provider
    
    try:
        # LangChain's generic initialization (langchain-core >= 0.2.x)
        # Supported providers: "openai", "anthropic", "google_genai", "mistralai", "groq", etc.
        model = init_chat_model(
            model=LLM_MODEL,
            model_provider=lc_provider,
            temperature=LLM_TEMPERATURE,
            api_key=LLM_API_KEY
        )
        return model
        
    except Exception as e:
        # Fallback to direct instantiation if init_chat_model dynamic mapping encounters issues
        import logging
        logging.getLogger(__name__).warning("init_chat_model failed, falling back to direct instantiation: %s", e)
        
        if lc_provider == "mistralai":
            from langchain_mistralai import ChatMistralAI
            return ChatMistralAI(model=LLM_MODEL, mistral_api_key=LLM_API_KEY, temperature=LLM_TEMPERATURE)
        elif lc_provider == "openai":
            from langchain_openai import ChatOpenAI
            return ChatOpenAI(model=LLM_MODEL, api_key=LLM_API_KEY, temperature=LLM_TEMPERATURE)
        elif lc_provider == "anthropic":
            from langchain_anthropic import ChatAnthropic
            return ChatAnthropic(model=LLM_MODEL, api_key=LLM_API_KEY, temperature=LLM_TEMPERATURE)
        elif lc_provider == "google_genai":
            from langchain_google_genai import ChatGoogleGenerativeAI
            return ChatGoogleGenerativeAI(model=LLM_MODEL, google_api_key=LLM_API_KEY, temperature=LLM_TEMPERATURE)
        elif lc_provider == "groq":
            from langchain_groq import ChatGroq
            return ChatGroq(model=LLM_MODEL, api_key=LLM_API_KEY, temperature=LLM_TEMPERATURE)
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")
