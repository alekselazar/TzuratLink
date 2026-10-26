from ..state import ChavrutaState


def finalize_answer(state: ChavrutaState) -> dict:
    if state.get("error"):
        return {"answer": f"Sorry, I couldn't process that: {state['error']}"}

    return {
        "answer": (state.get("answer") or "").strip(),
        "navigate_suggestion": state.get("navigate_suggestion"),
    }
