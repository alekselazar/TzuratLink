"""
Entry point the Django view calls. Owns Redis session state — loads prior
turns, streams the (stateless) graph, and persists the new exchange once it
completes. The graph itself never talks to Redis directly.
"""
from dataclasses import dataclass

from ..graph.builder import chavruta_graph
from .session_service import append_exchange, load_messages, new_session_id

# Only these nodes' LLM output is user-facing text worth streaming to the
# client — classify_intent also calls a model, but its structured-output
# JSON isn't something a user should see token-by-token.
_ANSWER_NODES = {
    "answer_summary", "answer_explanation", "answer_translation",
    "answer_rishonim", "answer_halacha", "answer_sources",
    "answer_vocabulary", "answer_quiz", "answer_navigate", "answer_general",
}


@dataclass(frozen=True)
class ChatRequest:
    user_id: int | None
    daf_ref: str
    question: str
    session_id: str | None = None
    explicit_mode: str | None = None


class ChavrutaChatService:
    def stream(self, request: ChatRequest):
        """
        Yields dicts describing the request's progress:
          {"type": "session", "session_id": ...}        — once, immediately
          {"type": "token", "content": ...}              — zero or more
          {"type": "done", "answer": ..., "intent": ..., "error": ...}  — once, last

        "done".answer is the authoritative final text (identical to what a
        plain .invoke() would have returned) — the streamed tokens are for
        a live-typing UI, but the accumulated tokens and "done".answer
        should match exactly in the success path.
        """
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

        yield {"type": "session", "session_id": session_id}

        final_answer = ""
        final_intent = initial_state.get("intent")
        final_error = None
        final_navigate_suggestion = None

        for mode, payload in chavruta_graph.stream(initial_state, stream_mode=["messages", "updates"]):
            if mode == "messages":
                chunk, metadata = payload
                if metadata.get("langgraph_node") in _ANSWER_NODES and chunk.content:
                    yield {"type": "token", "content": chunk.content}
            elif mode == "updates":
                for node_name, node_output in payload.items():
                    if not node_output:
                        continue
                    if "intent" in node_output:
                        final_intent = node_output["intent"]
                    if "error" in node_output:
                        final_error = node_output["error"]
                    if node_name == "finalize_answer":
                        final_answer = node_output.get("answer", "")
                        final_navigate_suggestion = node_output.get("navigate_suggestion")

        if not final_error:
            append_exchange(session_id, request.daf_ref, request.question, final_answer, final_intent)

        yield {
            "type": "done",
            "answer": final_answer,
            "intent": final_intent,
            "error": final_error,
            "navigate_suggestion": final_navigate_suggestion,
        }
