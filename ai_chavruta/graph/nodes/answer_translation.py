from ...prompts.translation import TRANSLATION_BRANCH_PROMPT
from ..state import ChavrutaState
from ._answer import run_answer_node


def answer_translation(state: ChavrutaState) -> dict:
    return run_answer_node(state, TRANSLATION_BRANCH_PROMPT)
