from ...prompts.summary import SUMMARY_BRANCH_PROMPT
from ..state import ChavrutaState
from ._answer import run_answer_node


def answer_summary(state: ChavrutaState) -> dict:
    return run_answer_node(state, SUMMARY_BRANCH_PROMPT)
