"""
Session continuity for chat requests. The graph itself is stateless per
call — this is what loads prior turns in before invoking it, and persists
the new exchange after.
"""
import uuid

from langchain_core.messages import AIMessage, HumanMessage

from ..cache.conversation_cache import get_session, save_session


def new_session_id():
    return str(uuid.uuid4())


def load_messages(session_id):
    session = get_session(session_id)
    if not session:
        return []

    messages = []
    for m in session.get("messages", []):
        if m["role"] == "user":
            messages.append(HumanMessage(content=m["content"]))
        else:
            messages.append(AIMessage(content=m["content"]))
    return messages


def append_exchange(session_id, daf_ref, question, answer, intent):
    session = get_session(session_id) or {"daf_ref": daf_ref, "messages": []}
    session["daf_ref"] = daf_ref
    session["messages"].append({"role": "user", "content": question})
    session["messages"].append({"role": "assistant", "content": answer, "intent": intent})
    save_session(session_id, session)
