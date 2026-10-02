"""Shared message-assembly + LLM-call logic for the answer_* nodes.
Not a graph node itself — each answer_*.py node calls this with its own
branch-specific prompt."""
from langchain_core.messages import HumanMessage, SystemMessage

from ...context.formatter import format_context_for_prompt
from ...llm.factory import get_chat_model
from ...prompts.base import BASE_CHAVRUTA_PROMPT
from ..state import ChavrutaState


def run_answer_node(state: ChavrutaState, branch_prompt: str) -> dict:
    context_text = format_context_for_prompt(state.get("selected_context", {}))

    messages = [
        SystemMessage(content=BASE_CHAVRUTA_PROMPT),
        SystemMessage(content=branch_prompt),
        SystemMessage(content=context_text),
        *state.get("messages", []),
        HumanMessage(content=state["question"]),
    ]

    response = get_chat_model().invoke(messages)
    return {"answer": response.content}
