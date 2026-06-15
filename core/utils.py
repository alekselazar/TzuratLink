from django.core.cache import cache

from .models import Page


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
