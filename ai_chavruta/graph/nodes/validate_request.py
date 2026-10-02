import re

from ..state import ChavrutaState

_DAF_REF_RE = re.compile(r"^.+?\s+\d+[ab]?$")


def validate_request(state: ChavrutaState) -> dict:
    if not state.get("daf_ref") or not _DAF_REF_RE.match(state["daf_ref"].strip()):
        return {"error": "A valid daf reference (e.g. 'Berakhot 2a') is required."}

    if not state.get("question") or not state["question"].strip():
        return {"error": "A question is required."}

    return {}
