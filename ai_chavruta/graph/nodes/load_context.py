import logging

from ...context.builder import build_daf_context
from ..state import ChavrutaState

logger = logging.getLogger(__name__)


def load_context(state: ChavrutaState) -> dict:
    try:
        full_context = build_daf_context(state["daf_ref"])
    except Exception:
        logger.exception("Failed to build daf context for %r", state["daf_ref"])
        return {"error": "Could not load the source material for this daf right now."}

    return {"full_context": full_context}
