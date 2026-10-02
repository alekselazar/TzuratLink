from ...prompts.explanation import EXPLANATION_BRANCH_PROMPT
from ..state import ChavrutaState
from ._answer import run_answer_node


def answer_explanation(state: ChavrutaState) -> dict:
    return run_answer_node(state, EXPLANATION_BRANCH_PROMPT)
