"""
Shared, cache-first client for the public Sefaria API.

Used by `reader` (per-ref lookups when a user clicks a bbox in the PDF viewer)
and by `ai_chavruta` (assembling daf context for the LLM). Both read through
the same Redis-backed cache, so a ref fetched by one feature is reused by the
other instead of hitting Sefaria twice.

Talmud/commentary text never changes once published, so successful lookups
are cached for a long time; failures are cached briefly so a slow or
unavailable Sefaria API never blocks or breaks a page render.
"""
import json
import logging
import urllib.parse
import urllib.request

from django.core.cache import cache

logger = logging.getLogger(__name__)

_SUCCESS_TTL = 60 * 60 * 24 * 30  # 30 days
_FAILURE_TTL = 60 * 60  # 1 hour
_SENTINEL = object()


def _fetch_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": "TzuratLink/1.0"})
    with urllib.request.urlopen(req, timeout=8) as response:
        return json.loads(response.read().decode("utf-8"))


def _cached_fetch(cache_key, url):
    cached = cache.get(cache_key, _SENTINEL)
    if cached is not _SENTINEL:
        return cached

    try:
        data = _fetch_json(url)
        cache.set(cache_key, data, _SUCCESS_TTL)
        return data
    except Exception:
        logger.warning("Sefaria fetch failed for %s", url, exc_info=True)
        cache.set(cache_key, None, _FAILURE_TTL)
        return None


def get_text_v3(ref, version=None):
    """
    Fetches a ref's text via Sefaria's v3 texts API (the version/text-only
    shape the reader UI renders). `version` selects a specific translation,
    e.g. "english|William Davidson Edition - English" — otherwise Sefaria
    returns its default (primary source-language) version. Returns the
    parsed JSON dict, or None if unavailable.
    """
    encoded_ref = urllib.parse.quote(ref)
    cache_key = f"sefaria:text_v3:{ref}:{version or 'default'}"
    url = f"https://www.sefaria.org/api/v3/texts/{encoded_ref}?return_format=text_only"
    if version:
        url += f"&version={urllib.parse.quote(version)}"
    return _cached_fetch(cache_key, url)


def get_links(ref):
    """
    Fetches the commentaries/cross-references linked to a ref (Rashi, Tosafot,
    Mishnah, etc. — Sefaria embeds each link's own text in the response, so no
    further per-link fetch is needed). Returns a list, or None if unavailable.
    """
    encoded_ref = urllib.parse.quote(ref)
    cache_key = f"sefaria:links:{ref}"
    url = f"https://www.sefaria.org/api/links/{encoded_ref}"
    return _cached_fetch(cache_key, url)
