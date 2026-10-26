from ...prompts.rishonim import RISHONIM_BRANCH_PROMPT
from ..state import ChavrutaState
from ._answer import run_answer_node


def answer_rishonim(state: ChavrutaState) -> dict:
    return run_answer_node(state, RISHONIM_BRANCH_PROMPT)
