from ...prompts.quiz import QUIZ_BRANCH_PROMPT
from ..state import ChavrutaState
from ._answer import run_answer_node


def answer_quiz(state: ChavrutaState) -> dict:
    return run_answer_node(state, QUIZ_BRANCH_PROMPT)
