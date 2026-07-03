import json
import logging
import urllib.parse
import urllib.request

from django.core.cache import cache
from django.utils.html import strip_tags

from .models import Page

logger = logging.getLogger(__name__)


def delete_page(page_id):
    try:
        page = Page.objects(id=page_id).first()
        if page:
            page.delete()
            return True
        return None
    except Exception:
        return None


def get_page(page_ref):
    try:
        return Page.objects(ref=page_ref).first()
    except Exception:
        return None


def get_for_sref(sefaria_ref):
    """
    Returns page data formatted for the frontend renderer.
    Uses Redis cache to speed up repeated requests.
    Returns None if page not found.
    """
    cache_key = f'page_data:{sefaria_ref}'
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    try:
        page = Page.objects(ref=sefaria_ref).first()
        if not page:
            return None

        result = {
            "pageId": str(page.id),
            "ref": page.ref,
            "sefaria_ref": page.effective_sefaria_ref(),
            "blocks": [block.to_dict() for block in (page.blocks or [])],
        }

        cache.set(cache_key, result, 3600)
        return result
    except Exception:
        return None


def get_sefaria_seo_text(sefaria_ref):
    """
    Fetches the Hebrew text of a ref from the public Sefaria API, for embedding
    as crawlable content in the initial page HTML (search engines see real daf
    text before/without executing JS; React replaces it on mount).

    Cached (including negative results, briefly) so a slow or unavailable
    Sefaria API never blocks or breaks a page render. Returns a list of plain
    text paragraphs, or None if unavailable.
    """
    if not sefaria_ref:
        return None

    cache_key = f'sefaria_seo_text:{sefaria_ref}'
    cached = cache.get(cache_key)
    if cached is not None:
        return cached or None

    try:
        encoded_ref = urllib.parse.quote(sefaria_ref)
        url = f'https://www.sefaria.org/api/texts/{encoded_ref}?context=0&commentary=0'
        req = urllib.request.Request(url, headers={'User-Agent': 'TzuratLink/1.0'})
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode('utf-8'))

        he = data.get('he') or []
        if isinstance(he, str):
            he = [he]
        paragraphs = [text for seg in he if (text := strip_tags(seg).strip())]

        cache.set(cache_key, paragraphs, 60 * 60 * 24)
        return paragraphs or None
    except Exception:
        logger.warning('Sefaria SEO text fetch failed for %s', sefaria_ref, exc_info=True)
        cache.set(cache_key, [], 60 * 60)
        return None
