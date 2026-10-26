from ...prompts.halacha import HALACHA_BRANCH_PROMPT
from ..state import ChavrutaState
from ._answer import run_answer_node


def answer_halacha(state: ChavrutaState) -> dict:
    return run_answer_node(state, HALACHA_BRANCH_PROMPT)
