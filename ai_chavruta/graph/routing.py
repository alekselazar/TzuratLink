from .state import ChavrutaState


def after_validate(state: ChavrutaState) -> str:
    if state.get("error"):
        return "finalize_answer"
    return "load_context"


def after_load_context(state: ChavrutaState) -> str:
    if state.get("error"):
        return "finalize_answer"
    return "classify_intent"


def route_by_intent(state: ChavrutaState) -> str:
    routes = {
        "summary": "answer_summary",
        "explanation": "answer_explanation",
        "translation": "answer_translation",
        "rishonim": "answer_rishonim",
        "halacha": "answer_halacha",
        "sources": "answer_sources",
        "vocabulary": "answer_vocabulary",
        "quiz": "answer_quiz",
        "navigate": "answer_navigate",
    }
    return routes.get(state.get("intent"), "answer_general")
