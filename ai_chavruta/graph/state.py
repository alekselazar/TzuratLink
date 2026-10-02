from typing import Any, Literal, NotRequired, TypedDict

from langchain_core.messages import BaseMessage

ChavrutaIntent = Literal[
    "summary",
    "explanation",
    "translation",
    "rishonim",
    "halacha",
    "sources",
    "vocabulary",
    "quiz",
    "general",
]


class ChavrutaState(TypedDict):
    # Request identity
    user_id: int | None
    session_id: str
    daf_ref: str

    # User input
    question: str
    messages: list[BaseMessage]

    # Intent routing — explicit_mode (an explicit UI button, e.g. "Summarize
    # daf") pre-sets "intent" before the graph runs, letting classify_intent
    # skip the LLM call entirely.
    intent: NotRequired[ChavrutaIntent]
    intent_confidence: NotRequired[float]

    # Context
    full_context: NotRequired[dict[str, Any]]
    selected_context: NotRequired[dict[str, Any]]

    # Output
    answer: NotRequired[str]

    # Control data
    error: NotRequired[str]
