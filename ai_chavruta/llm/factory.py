"""
Two OpenAI model tiers: a cheap/fast default for most branches, and a
stronger reasoning model for branches that need real multi-source synthesis.
See model_router.py for which intents use which tier.
"""
from django.conf import settings
from langchain_openai import ChatOpenAI, OpenAIEmbeddings


def get_chat_model(temperature=0.2):
    return ChatOpenAI(
        model=settings.AI_CHAVRUTA_MODEL,
        api_key=settings.OPENAI_API_KEY,
        temperature=temperature,
    )


def get_reasoning_model(temperature=0.2):
    return ChatOpenAI(
        model=settings.AI_CHAVRUTA_REASONING_MODEL,
        api_key=settings.OPENAI_API_KEY,
        temperature=temperature,
    )


def get_embeddings():
    return OpenAIEmbeddings(
        model=settings.AI_CHAVRUTA_EMBEDDING_MODEL,
        api_key=settings.OPENAI_API_KEY,
    )
