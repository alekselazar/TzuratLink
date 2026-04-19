from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from django.core.cache import cache
import json
import urllib.request
from core.utils import get_for_sref, generate_page_metadata
from core.language import get_language_from_header, get_language_direction


def health(request):
    """Simple health check for Docker/load balancers; no redirect, no DB."""
    return HttpResponse("ok", content_type="text/plain")


def index(request):
    return redirect('dafyomi_redirect')


def dafyomi_redirect(request):
    """
    Redirect /dafyomi/ to today's Daf Yomi page.
    Fetches today's Daf Yomi reference from Sefaria API and redirects.
    """
    if request.method != 'GET':
        return JsonResponse({'error': "You are not permitted"}, status=403)
    
    try:
        req = urllib.request.Request('https://www.sefaria.org/api/calendars')
        with urllib.request.urlopen(req, timeout=5) as response:
            data = response.read()
            encoding = response.headers.get_content_charset('utf-8')
            json_data = json.loads(data.decode(encoding))
        
        for item in json_data['calendar_items']:
            if item['title']['en'] == 'Daf Yomi':
                ref = item['ref']
                # Default to amud 'a'
                ref += 'a'
                return redirect('page_view', ref=ref)
        
        # Fallback if Daf Yomi not found
        return JsonResponse({'error': "Daf Yomi not found"}, status=404)
    
    except urllib.error.URLError as e:
        return JsonResponse({'error': "Failed to fetch Daf Yomi reference"}, status=503)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def page_view(request, ref):
    """
    Generic page view for any page reference.
    Renders a page with given Sefaria reference and SEO metadata.
    Detects user language from Accept-Language header.
    """
    if request.method != 'GET':
        return JsonResponse({'error': "You are not permitted"}, status=403)
    
    # Detect user language from Accept-Language header
    accept_language = request.META.get('HTTP_ACCEPT_LANGUAGE', 'he')
    lang = get_language_from_header(accept_language)
    direction = get_language_direction(lang)
    
    # Fetch page data (cached)
    page_data = get_for_sref(ref)
    
    if page_data is None:
        return JsonResponse({'error': "Page not found"}, status=404)
    
    # Try to get cached metadata first
    meta_cache_key = f'page_meta:{ref}'
    meta = cache.get(meta_cache_key)
    
    if meta is None:
        # Generate SEO metadata and structured data
        meta = generate_page_metadata(ref, page_data)
        # Cache metadata for 24 hours
        cache.set(meta_cache_key, meta, 86400)

    # Return CSR template with SEO data
    return render(request,
                'reader.html',
                context={
                    'lang': lang,
                    'direction': direction,
                    'component': json.dumps('PDFReader'),
                    'props': json.dumps(page_data),
                    'page_title': meta['title'],
                    'page_description': meta['description'],
                    'page_image': meta['image_url'],
                    'canonical_url': meta['canonical_url'],
                    'structured_data': json.dumps(meta['structured_data']),
                    'ref': ref
                })


def reader_catchall(request, path=''):
    """
    Catch-all route for client-side routing.
    Serves the React app for any routes not explicitly handled by Django.
    Default: redirect to Daf Yomi.
    """
    return redirect('dafyomi_redirect')


def get_page_data(request, ref):
    """
    API endpoint for client-side data fetching.
    """
    if request.method != 'GET':
        return JsonResponse({'error': "Method not allowed"}, status=405)
    
    page_data = get_for_sref(ref)
    
    if page_data is None:
        return JsonResponse({'error': "Page not found"}, status=404)
    
    return JsonResponse(page_data)


def get_next_page(request, ref):
    """
    API endpoint to get the next page reference.
    For Daf Yomi pages:
    - If ends with 'a', next is same page with 'b'
    - If ends with 'b', next needs to be fetched from Sefaria
    
    Returns: {ref: string, exists: bool}
    """
    if request.method != 'GET':
        return JsonResponse({'error': "Method not allowed"}, status=405)
    
    try:
        # Check if this is an amud (ends with 'a' or 'b')
        if ref.endswith('a'):
            # Next is 'b' of same page
            next_ref = ref[:-1] + 'b'
            # Verify it exists
            page_data = get_for_sref(next_ref)
            exists = page_data is not None
            return JsonResponse({'ref': next_ref, 'exists': exists})
        
        elif ref.endswith('b'):
            # Next page after 'b' - need to ask Sefaria for next page
            # For now, return null as we don't have a simple way to get next without full logic
            return JsonResponse({'ref': None, 'exists': False})
        
        else:
            return JsonResponse({'error': "Reference doesn't end with amud (a/b)"}, status=400)
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def get_prev_page(request, ref):
    """
    API endpoint to get the previous page reference.
    For Daf Yomi pages:
    - If ends with 'b', previous is same page with 'a'
    - If ends with 'a', previous needs to be fetched from Sefaria
    
    Returns: {ref: string, exists: bool}
    """
    if request.method != 'GET':
        return JsonResponse({'error': "Method not allowed"}, status=405)
    
    try:
        # Check if this is an amud (ends with 'a' or 'b')
        if ref.endswith('b'):
            # Previous is 'a' of same page
            prev_ref = ref[:-1] + 'a'
            # Verify it exists
            page_data = get_for_sref(prev_ref)
            exists = page_data is not None
            return JsonResponse({'ref': prev_ref, 'exists': exists})
        
        elif ref.endswith('a'):
            # Previous page before 'a' - need to ask Sefaria for prev page
            # For now, return null as we don't have a simple way to get prev without full logic
            return JsonResponse({'ref': None, 'exists': False})
        
        else:
            return JsonResponse({'error': "Reference doesn't end with amud (a/b)"}, status=400)
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


