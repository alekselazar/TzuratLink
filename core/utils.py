from django.core.cache import cache

from .models import Page

def delete_page(page_id):
    try:
        page = Page.objects(id=page_id).first()
        if page:
            # Cache invalidation is handled automatically by signals in core/apps.py
            page.delete()
            return True
        return None
    except Exception:
        return None

def get_page(page_ref):
    try:
        page = Page.objects(ref=page_ref).first()
        return page
    except Exception:
        return None

def get_for_sref(sefaria_ref):
    """
    Get page data from MongoDB for a given ref.
    Returns data formatted for React components (keys: pageId, pdfUrl, boxes, anchors).
    Uses Redis cache to speed up repeated requests.
    Returns None if page not found.
    """
    # Check cache first
    cache_key = f'page_data:{sefaria_ref}'
    cached_data = cache.get(cache_key)
    if cached_data is not None:
        return cached_data
    
    try:
        # Query MongoDB for page by ref
        page = Page.objects(ref=sefaria_ref).first()
        if not page:
            return None
        
        boxes = []
        for bbox in page.bboxes or []:
            boxes.append({
                "ref": bbox.ref,
                "top": f"{float(bbox.top) * 100}%",
                "left": f"{float(bbox.left) * 100}%",
                "width": f"{float(bbox.width) * 100}%",
                "height": f"{float(bbox.height) * 100}%",
            })

        result = {
            "pageId": str(page.id),
            "ref": page.ref,
            "sefaria_ref": page.effective_sefaria_ref(),
            "pdfUrl": page.source_pdf,
            "boxes": boxes,
            "anchors": [],
        }
        
        # Cache the result for 1 hour (3600 seconds)
        cache.set(cache_key, result, 3600)
        
        return result
    except Exception:
        return None

