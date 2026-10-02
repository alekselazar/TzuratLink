"""
Redis-backed conversation history per chat session. No Postgres — session
data is intentionally ephemeral (30-day TTL, refreshed on every write)
rather than a durable DB row.
"""
from django.core.cache import cache

from .keys import session_key

SESSION_TTL = 60 * 60 * 24 * 30  # 30 days


def get_session(session_id):
    return cache.get(session_key(session_id))


def save_session(session_id, session_data):
    cache.set(session_key(session_id), session_data, SESSION_TTL)
