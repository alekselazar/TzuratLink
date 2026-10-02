from langgraph.graph import END, START, StateGraph

from .nodes.answer_explanation import answer_explanation
from .nodes.answer_general import answer_general
from .nodes.answer_summary import answer_summary
from .nodes.classify_intent import classify_intent
from .nodes.finalize_answer import finalize_answer
from .nodes.load_context import load_context
from .nodes.select_context import select_context
from .nodes.validate_request import validate_request
from .routing import after_load_context, after_validate, route_by_intent
from .state import ChavrutaState


def build_chavruta_graph():
    graph = StateGraph(ChavrutaState)

    graph.add_node("validate_request", validate_request)
    graph.add_node("load_context", load_context)
    graph.add_node("classify_intent", classify_intent)
    graph.add_node("select_context", select_context)
    graph.add_node("answer_summary", answer_summary)
    graph.add_node("answer_explanation", answer_explanation)
    graph.add_node("answer_general", answer_general)
    graph.add_node("finalize_answer", finalize_answer)

    graph.add_edge(START, "validate_request")

    graph.add_conditional_edges(
        "validate_request",
        after_validate,
        {"load_context": "load_context", "finalize_answer": "finalize_answer"},
    )

    graph.add_conditional_edges(
        "load_context",
        after_load_context,
        {"classify_intent": "classify_intent", "finalize_answer": "finalize_answer"},
    )

    graph.add_edge("classify_intent", "select_context")

    graph.add_conditional_edges(
        "select_context",
        route_by_intent,
        {
            "answer_summary": "answer_summary",
            "answer_explanation": "answer_explanation",
            "answer_general": "answer_general",
        },
    )

    for node in ("answer_summary", "answer_explanation", "answer_general"):
        graph.add_edge(node, "finalize_answer")

    graph.add_edge("finalize_answer", END)

    return graph.compile()


chavruta_graph = build_chavruta_graph()
