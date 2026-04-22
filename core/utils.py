import threading
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
    except Exception as e:
        return None

def get_page(page_ref):
    try:
        page = Page.objects(ref=page_ref).first()
        return page
    except Exception as e:
        return None

def get_for_sref(sefaria_ref):
    """
    Get page data from MongoDB for a given Sefaria reference.
    Returns data formatted for React components.
    Uses Redis cache to speed up repeated requests.
    
    Args:
        sefaria_ref: Sefaria reference string (e.g., "Berakhot:2a")
    
    Returns:
        dict with keys: pageId, file, boxes, anchors
        Returns None if page not found
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
        
        # Use stored PNG base64 from MongoDB (page.base64_data)
        if not page.base64_data or not page.base64_data.strip():
            return None
        
        # Convert bboxes to format expected by React (with sefaria_ref instead of ref)
        # Coordinates are floats in [0,1], convert to percent strings for CSS
        boxes = []
        for bbox in page.bboxes or []:
            boxes.append({
                "sefaria_ref": bbox.ref,
                "top": f"{float(bbox.top) * 100}%",
                "left": f"{float(bbox.left) * 100}%",
                "width": f"{float(bbox.width) * 100}%",
                "height": f"{float(bbox.height) * 100}%",
            })
        
        # Return data in format expected by React components (file = PNG base64)
        result = {
            "pageId": str(page.id),
            "file": page.base64_data.strip(),
            "boxes": boxes,
            "anchors": []  # Empty for now, can be populated if needed
        }
        
        # Cache the result for 1 hour (3600 seconds)
        cache.set(cache_key, result, 3600)
        
        return result
    except Exception as e:
        return None

def get_for_sref_with_timeout(sefaria_ref, timeout=2.0):
    """
    Get page data from MongoDB with a timeout for SSR/CSR decision.
    If data can be fetched within timeout, returns the data (SSR).
    If timeout is exceeded, returns {'timeout': True, 'ref': sefaria_ref} (CSR fallback).
    
    Args:
        sefaria_ref: Sefaria reference string (e.g., "Berakhot:2a")
        timeout: Maximum time in seconds to wait (default: 2.0)
    
    Returns:
        dict with page data if successful, or {'timeout': True, 'ref': sefaria_ref} if timeout
    """
    result = {'timeout': False, 'data': None}
    exception_occurred = [False]
    
    def fetch_data():
        try:
            data = get_for_sref(sefaria_ref)
            result['data'] = data
        except Exception as e:
            exception_occurred[0] = True
            result['data'] = None
    
    # Start fetching in a thread
    thread = threading.Thread(target=fetch_data)
    thread.daemon = True
    thread.start()
    thread.join(timeout=timeout)
    
    if thread.is_alive():
        # Timeout occurred
        return {'timeout': True, 'ref': sefaria_ref}
    
    if exception_occurred[0] or result['data'] is None:
        return None
    
    return result['data']