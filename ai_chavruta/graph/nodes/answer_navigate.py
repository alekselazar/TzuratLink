"""Unlike the other answer_* nodes, this one does real tool/function
calling: it retrieves candidate dapim from the Shas vector index first,
then lets the model choose among them (or decline) via a dynamically
schema-constrained select_daf tool — it cannot "navigate" anywhere that
wasn't actually retrieved."""
import logging

from langchain_core.messages import HumanMessage, SystemMessage

from ...llm.model_router import get_model_for_intent
from ...llm.tools import build_select_daf_tool
from ...prompts.base import BASE_CHAVRUTA_PROMPT
from ...prompts.navigate import NAVIGATE_BRANCH_PROMPT
from ...retrieval.shas_index import search_shas
from ..state import ChavrutaState

logger = logging.getLogger(__name__)

NO_CANDIDATES_FALLBACK = (
    "I couldn't find a specific place in Shas for that — could you tell me "
    "a bit more about what you're looking for?"
)


def _format_candidates(candidates):
    lines = []
    for c in candidates:
        lines.append(f"- {c.ref} — {c.subject}: {c.text[:300]}")
    return "Retrieved candidate passages:\n" + "\n".join(lines)


def answer_navigate(state: ChavrutaState) -> dict:
    try:
        candidates = search_shas(state["question"])
    except Exception:
        logger.exception("Shas retrieval failed")
        return {"error": "The assistant is temporarily unavailable. Please try again."}

    if not candidates:
        return {"answer": NO_CANDIDATES_FALLBACK, "navigate_suggestion": None}

    candidate_refs = list(dict.fromkeys(c.ref for c in candidates))
    select_daf_tool = build_select_daf_tool(candidate_refs)
    candidates_by_ref = {c.ref: c for c in candidates}

    messages = [
        SystemMessage(content=BASE_CHAVRUTA_PROMPT),
        SystemMessage(content=NAVIGATE_BRANCH_PROMPT),
        SystemMessage(content=_format_candidates(candidates)),
        *state.get("messages", []),
        HumanMessage(content=state["question"]),
    ]

    try:
        model = get_model_for_intent(state.get("intent")).bind_tools([select_daf_tool])
        response = model.invoke(messages)
    except Exception:
        logger.exception("Navigate answer generation failed")
        return {"error": "The assistant is temporarily unavailable. Please try again."}

    suggestion = None
    for call in response.tool_calls or []:
        if call["name"] != "SelectDaf":
            continue
        try:
            args = select_daf_tool(**call["args"])
        except Exception:
            logger.warning("Model called select_daf with invalid args: %r", call.get("args"))
            continue
        chosen = candidates_by_ref.get(args.ref)
        if chosen:
            suggestion = {"ref": args.ref, "subject": chosen.subject, "reason": args.reason}
        break

    answer = (response.content or "").strip()
    if not answer:
        answer = (
            f"That's discussed in {suggestion['ref']} ({suggestion['subject']})."
            if suggestion else NO_CANDIDATES_FALLBACK
        )

    return {"answer": answer, "navigate_suggestion": suggestion}
