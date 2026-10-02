"""
Single OpenAI chat model factory. One model tier for now (per
settings.AI_CHAVRUTA_MODEL) — multi-tier routing (cheap classifier model vs.
stronger reasoning model) is a later-phase optimization, not needed to prove
the graph out.
"""
from django.conf import settings
from langchain_openai import ChatOpenAI


def get_chat_model(temperature=0.2):
    return ChatOpenAI(
        model=settings.AI_CHAVRUTA_MODEL,
        api_key=settings.OPENAI_API_KEY,
        temperature=temperature,
    )
