from ...prompts.general import GENERAL_BRANCH_PROMPT
from ..state import ChavrutaState
from ._answer import run_answer_node


def answer_general(state: ChavrutaState) -> dict:
    return run_answer_node(state, GENERAL_BRANCH_PROMPT)
