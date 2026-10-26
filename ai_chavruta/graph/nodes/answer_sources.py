from ...prompts.sources import SOURCES_BRANCH_PROMPT
from ..state import ChavrutaState
from ._answer import run_answer_node


def answer_sources(state: ChavrutaState) -> dict:
    return run_answer_node(state, SOURCES_BRANCH_PROMPT)
