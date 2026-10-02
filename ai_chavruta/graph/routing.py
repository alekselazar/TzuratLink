from .state import ChavrutaState


def after_validate(state: ChavrutaState) -> str:
    if state.get("error"):
        return "finalize_answer"
    return "load_context"


def after_load_context(state: ChavrutaState) -> str:
    if state.get("error"):
        return "finalize_answer"
    return "classify_intent"


# Thin slice: only summary/explanation have dedicated branches so far.
# Every other intent (translation/rishonim/halacha/sources/vocabulary/quiz/
# general) falls back to the general chavruta-discussion node until its own
# branch is built.
def route_by_intent(state: ChavrutaState) -> str:
    routes = {
        "summary": "answer_summary",
        "explanation": "answer_explanation",
    }
    return routes.get(state.get("intent"), "answer_general")
