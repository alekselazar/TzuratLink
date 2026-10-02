"""
Entry point the Django view calls. Owns Redis session state — loads prior
turns, invokes the (stateless) graph, and persists the new exchange. The
graph itself never talks to Redis directly.
"""
from dataclasses import dataclass

from ..graph.builder import chavruta_graph
from .session_service import append_exchange, load_messages, new_session_id


@dataclass(frozen=True)
class ChatRequest:
    user_id: int | None
    daf_ref: str
    question: str
    session_id: str | None = None
    explicit_mode: str | None = None


class ChavrutaChatService:
    def invoke(self, request: ChatRequest) -> dict:
        session_id = request.session_id or new_session_id()
        history = load_messages(session_id)

        initial_state = {
            "user_id": request.user_id,
            "session_id": session_id,
            "daf_ref": request.daf_ref,
            "question": request.question,
            "messages": history,
        }
        if request.explicit_mode:
            initial_state["intent"] = request.explicit_mode

        result = chavruta_graph.invoke(initial_state)

        answer = result.get("answer", "")
        intent = result.get("intent")
        error = result.get("error")

        if not error:
            append_exchange(session_id, request.daf_ref, request.question, answer, intent)

        return {
            "session_id": session_id,
            "answer": answer,
            "intent": intent,
            "error": error,
        }
