"""Shared message-assembly + LLM-call logic for the answer_* nodes.
Not a graph node itself — each answer_*.py node calls this with its own
branch-specific prompt."""
import logging

from langchain_core.messages import HumanMessage, SystemMessage

from ...context.formatter import format_context_for_prompt
from ...llm.factory import get_chat_model
from ...prompts.base import BASE_CHAVRUTA_PROMPT
from ..state import ChavrutaState

logger = logging.getLogger(__name__)


def run_answer_node(state: ChavrutaState, branch_prompt: str) -> dict:
    context_text = format_context_for_prompt(state.get("selected_context", {}))

    messages = [
        SystemMessage(content=BASE_CHAVRUTA_PROMPT),
        SystemMessage(content=branch_prompt),
        SystemMessage(content=context_text),
        *state.get("messages", []),
        HumanMessage(content=state["question"]),
    ]

    try:
        response = get_chat_model().invoke(messages)
    except Exception:
        logger.exception("Answer generation failed")
        return {"error": "The assistant is temporarily unavailable. Please try again."}

    return {"answer": response.content}
