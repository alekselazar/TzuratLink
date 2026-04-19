from django.core.cache import cache
from django.conf import settings

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
        
        # Return data in format expected by React components
        result = {
            "pageId": str(page.id),
            "ref": page.ref,
            "hebrew_title": page.hebrew_title,
            "pdfUrl": page.source_pdf,
            "boxes": boxes,
            "anchors": []
        }
        
        # Cache the result for 1 hour (3600 seconds)
        cache.set(cache_key, result, 3600)
        
        return result
    except Exception as e:
        return None


def generate_page_metadata(sefaria_ref, page_data=None):
    """
    Generate SEO metadata and structured data for a page.
    Used for meta tags and JSON-LD in HTML responses.
    
    Args:
        sefaria_ref: Sefaria reference string (e.g., "Berakhot:2a")
        page_data: Page data dict from get_for_sref()
    
    Returns:
        dict with title, description, image_url, canonical_url, structured_data
    """
    from django.urls import reverse
    
    site_url = getattr(settings, 'SITE_URL', 'http://localhost:8000').rstrip('/')
    
    # Extract amud from ref
    amud = 'a' if sefaria_ref.endswith('a') else 'b'
    
    # Get page object for hebrew_title
    try:
        page = Page.objects(ref=sefaria_ref).first()
        hebrew_title = page.hebrew_title if page and page.hebrew_title else None
    except:
        hebrew_title = None
    
    # Generate meta tags
    title = f"{sefaria_ref} | TzuratLink"
    if hebrew_title:
        title = f"{hebrew_title} - {sefaria_ref} | TzuratLink"
    
    description = f"Study Talmud page {sefaria_ref} with footnotes and Sefaria references on TzuratLink"
    
    image_url = ''  # No embedded image; OG image can be a static asset if needed
    
    # Generate canonical URL
    canonical_url = f"{site_url}/dafyomi/{amud}"
    
    # Generate JSON-LD structured data for Google
    structured_data = {
        "@context": "https://schema.org",
        "@type": "ScholarlyArticle",
        "headline": title,
        "description": description,
        "url": canonical_url,
        "image": {
            "@type": "ImageObject",
            "url": image_url[:200] if image_url else ""  # Limit length
        },
        "datePublished": "2024-01-01",
        "dateModified": "2024-01-01",
        "author": {
            "@type": "Organization",
            "name": "TzuratLink"
        },
        "publisher": {
            "@type": "Organization",
            "name": "TzuratLink",
            "logo": {
                "@type": "ImageObject",
                "url": f"{site_url}/static/img/logo.png"
            }
        },
        "mainEntity": {
            "@type": "Book",
            "name": "Talmud - " + sefaria_ref,
            "author": {
                "@type": "Organization",
                "name": "Rabbinic tradition"
            }
        }
    }
    
    return {
        'title': title,
        'description': description,
        'image_url': image_url,
        'canonical_url': canonical_url,
        'structured_data': structured_data
    }


def prerender_page(sefaria_ref, cache_duration=86400):
    """
    Pre-render and cache a page (warm cache).
    
    Args:
        sefaria_ref: Sefaria reference string (e.g., "Berakhot:2a")
        cache_duration: How long to keep in cache (default: 24 hours)
    
    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        page_data = get_for_sref(sefaria_ref)
        
        if page_data is None:
            return False, f"Page not found: {sefaria_ref}"
        
        # Cache with longer duration for pre-rendered pages
        cache_key = f'page_data:{sefaria_ref}'
        cache.set(cache_key, page_data, cache_duration)
        
        # Also generate and cache metadata
        metadata = generate_page_metadata(sefaria_ref, page_data)
        meta_cache_key = f'page_meta:{sefaria_ref}'
        cache.set(meta_cache_key, metadata, cache_duration)
        
        return True, f"Pre-rendered {sefaria_ref}"
    except Exception as e:
        return False, f"Error pre-rendering {sefaria_ref}: {str(e)}"


def prerender_daf_yomi(cache_duration=86400):
    """
    Pre-render today's Daf Yomi pages (both amud a and b).
    Call this on app startup or via scheduled task.
    
    Args:
        cache_duration: How long to keep in cache (default: 24 hours)
    
    Returns:
        dict: {ref: (success, message), ...}
    """
    import urllib.request
    import json
    
    results = {}
    
    try:
        # Fetch today's Daf Yomi reference from Sefaria API
        req = urllib.request.Request('https://www.sefaria.org/api/calendars')
        with urllib.request.urlopen(req, timeout=5) as response:
            data = response.read()
            encoding = response.headers.get_content_charset('utf-8')
            json_data = json.loads(data.decode(encoding))
        
        daf_yomi_ref = None
        for item in json_data.get('calendar_items', []):
            if item.get('title', {}).get('en') == 'Daf Yomi':
                daf_yomi_ref = ':'.join(item['ref'].split(' '))
                break
        
        if not daf_yomi_ref:
            return {'error': 'Could not fetch today\'s Daf Yomi'}
        
        # Pre-render both amud a and b
        for amud in ['a', 'b']:
            ref = daf_yomi_ref + amud
            success, message = prerender_page(ref, cache_duration)
            results[ref] = (success, message)
    
    except Exception as e:
        results['error'] = f"Error fetching Daf Yomi: {str(e)}"
    
    return results


def get_all_available_pages():
    """
    Get list of all available page references in MongoDB.
    Useful for batch pre-rendering.
    
    Returns:
        list: List of page ref strings
    """
    try:
        pages = Page.objects.only('ref')
        return [page.ref for page in pages if page.ref]
    except Exception as e:
        return []


def prerender_all_pages(cache_duration=604800, limit=None):
    """
    Pre-render all available pages (for full cache warming).
    This can be resource-intensive for large datasets.
    
    Args:
        cache_duration: How long to keep in cache (default: 7 days)
        limit: Maximum pages to pre-render (None = all)
    
    Returns:
        dict: {ref: (success, message), ...}
    """
    results = {}
    pages = get_all_available_pages()
    
    if limit:
        pages = pages[:limit]
    
    for i, ref in enumerate(pages):
        success, message = prerender_page(ref, cache_duration)
        results[ref] = (success, message)
        
        if (i + 1) % 10 == 0:
            print(f"Pre-rendered {i + 1}/{len(pages)} pages...")
    
    return results