"""Redis cache key builders for ai_chavruta."""

CONTEXT_CACHE_VERSION = "v1"
SESSION_CACHE_VERSION = "v1"


def daf_context_key(daf_ref):
    return f"chavruta:context:{CONTEXT_CACHE_VERSION}:{daf_ref}"


def session_key(session_id):
    return f"chavruta:session:{SESSION_CACHE_VERSION}:{session_id}"
