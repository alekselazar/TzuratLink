"""Redis cache for the fully assembled, parsed daf context (see context/builder.py)."""
from django.core.cache import cache

from .keys import daf_context_key

CONTEXT_TTL = 60 * 60 * 24 * 30  # 30 days — Talmud text is static


def get_cached_context(daf_ref):
    return cache.get(daf_context_key(daf_ref))


def set_cached_context(daf_ref, context):
    cache.set(daf_context_key(daf_ref), context, CONTEXT_TTL)
