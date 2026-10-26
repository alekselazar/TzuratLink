from ...prompts.vocabulary import VOCABULARY_BRANCH_PROMPT
from ..state import ChavrutaState
from ._answer import run_answer_node


def answer_vocabulary(state: ChavrutaState) -> dict:
    return run_answer_node(state, VOCABULARY_BRANCH_PROMPT)
