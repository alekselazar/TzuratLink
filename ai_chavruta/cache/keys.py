"""Redis cache key builders for ai_chavruta."""

CONTEXT_CACHE_VERSION = "v1"


def daf_context_key(daf_ref):
    return f"chavruta:context:{CONTEXT_CACHE_VERSION}:{daf_ref}"
