from ...context.selectors import select_context as select_context_sections
from ..state import ChavrutaState


def select_context(state: ChavrutaState) -> dict:
    selected = select_context_sections(state["full_context"], state["intent"])
    return {"selected_context": selected}
