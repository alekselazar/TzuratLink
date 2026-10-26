"""Real LangChain tool schemas (bound via `.bind_tools()`), as opposed to the
JSON-Schema structured-output mode used by classify_intent — the model
dynamically decides whether to call these based on the conversation."""
from typing import Literal

from pydantic import create_model, Field


def build_select_daf_tool(candidate_refs):
    """Builds a SelectDaf tool whose `ref` field is constrained (at the
    schema level, not just by prompt instruction) to the given refs — the
    model can only "navigate" to a daf that was actually retrieved, never
    one it recalls on its own."""
    return create_model(
        "SelectDaf",
        __doc__=(
            "Call this to point the student to one of the retrieved candidate "
            "dapim, if one of them actually answers their question."
        ),
        ref=(Literal[tuple(candidate_refs)], Field(description="One of the retrieved candidate refs")),
        reason=(str, Field(description="One short sentence on why this is the place")),
    )
