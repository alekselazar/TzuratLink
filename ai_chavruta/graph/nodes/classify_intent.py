import logging

from langchain_core.messages import HumanMessage, SystemMessage

from ...llm.factory import get_chat_model
from ...llm.structured_outputs import IntentClassification
from ...prompts.classifier import CLASSIFIER_PROMPT
from ..state import ChavrutaState

logger = logging.getLogger(__name__)


def classify_intent(state: ChavrutaState) -> dict:
    # An explicit UI mode (e.g. a "Summarize daf" button) pre-sets intent
    # before the graph runs — skip the classifier call entirely.
    if state.get("intent"):
        return {}

    recent_turns = state.get("messages", [])[-2:]
    history_text = "\n".join(f"{m.type}: {m.content}" for m in recent_turns)

    user_content = (
        f"Daf: {state['daf_ref']}\n"
        f"Recent conversation:\n{history_text or '(none)'}\n"
        f"Question: {state['question']}"
    )

    try:
        model = get_chat_model(temperature=0).with_structured_output(IntentClassification)
        result: IntentClassification = model.invoke([
            SystemMessage(content=CLASSIFIER_PROMPT),
            HumanMessage(content=user_content),
        ])
    except Exception:
        logger.exception("Intent classification failed; falling back to general")
        return {"intent": "general", "intent_confidence": 0.0}

    return {"intent": result.intent, "intent_confidence": result.confidence}
