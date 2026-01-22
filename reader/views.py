from django.shortcuts import render, redirect
from django.http import JsonResponse
import json
import urllib.request
import threading
from core.utils import get_for_sref, get_for_sref_with_timeout

def index(request):
    return redirect('daf yomi')

def daf_yomi(request, amud='a'):
    if request.method != 'GET':
        return JsonResponse({'error': "You are not permitted"}, status=403)
    
    req = urllib.request.Request('https://www.sefaria.org/api/calendars')
    with urllib.request.urlopen(req) as response:
        data = response.read()
        encoding = response.headers.get_content_charset('utf-8')
        json_data = json.loads(data.decode(encoding)) 
    for item in json_data['calendar_items']:
        if item['title']['en'] == 'Daf Yomi':
            ref = ':'.join(item['ref'].split(' '))

    if amud == 'a':
        ref += 'a'
    elif amud == 'b':
        ref += 'b'
    else:
        return JsonResponse({'error': "Amud should be a or b"}, status=404)
    
    # Try SSR with timeout (2 seconds)
    page_data = get_for_sref_with_timeout(ref, timeout=2.0)
    
    # Check if timeout occurred (CSR fallback needed)
    if isinstance(page_data, dict) and page_data.get('timeout'):
        # Return minimal data for CSR
        return render(request,
                    'dafyomi.html',
                    context={
                        'amud': amud,
                        'component': json.dumps('PDFReader'),
                        'props': json.dumps({
                            'csr': True,
                            'ref': ref
                        }),
                        'ssr_html': None
                    })
    
    if page_data is None:
        return JsonResponse({'error': "Page not found"}, status=404)

    # Try to get SSR HTML from Node.js server
    ssr_html = None
    try:
        ssr_html = get_ssr_html('PDFReader', page_data, timeout=1.0)
    except Exception as e:
        # If SSR fails, continue with CSR
        print(f"SSR failed: {e}")
        pass

    # Return with SSR HTML if available, otherwise CSR
    return render(request,
                'dafyomi.html',
                context={
                    'amud': amud,
                    'component': json.dumps('PDFReader'),
                    'props': json.dumps(page_data),
                    'ssr_html': ssr_html
                })

def get_page_data(request, ref):
    """
    API endpoint for client-side data fetching (CSR fallback).
    """
    if request.method != 'GET':
        return JsonResponse({'error': "Method not allowed"}, status=405)
    
    page_data = get_for_sref(ref)
    
    if page_data is None:
        return JsonResponse({'error': "Page not found"}, status=404)
    
    return JsonResponse(page_data)

def get_ssr_html(component, props, timeout=1.0):
    """
    Get server-side rendered HTML from Node.js server.
    Returns HTML string or None if timeout/failure.
    """
    try:
        result = {'html': None, 'error': None}
        
        def fetch_ssr():
            try:
                data = json.dumps({
                    'component': component,
                    'props': props
                }).encode('utf-8')
                
                req = urllib.request.Request(
                    'http://localhost:3000/render',
                    data=data,
                    headers={
                        'Content-Type': 'application/json',
                        'Content-Length': str(len(data))
                    }
                )
                
                with urllib.request.urlopen(req, timeout=timeout) as response:
                    response_data = json.loads(response.read().decode('utf-8'))
                    result['html'] = response_data.get('html')
            except Exception as e:
                result['error'] = str(e)
        
        thread = threading.Thread(target=fetch_ssr)
        thread.daemon = True
        thread.start()
        thread.join(timeout=timeout + 0.5)
        
        if thread.is_alive():
            return None
        
        return result['html']
    except Exception as e:
        return None
