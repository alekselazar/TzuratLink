import re as re_module
import json
import urllib.request
import urllib.error

from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.conf import settings

from core.utils import get_for_sref, get_sefaria_seo_text


def _lang(request):
    accept = request.META.get('HTTP_ACCEPT_LANGUAGE', 'he')
    tag = accept.split(',')[0].split(';')[0].strip().split('-')[0].lower()
    return tag[:2] if tag else 'he'


def _dir(lang):
    return 'ltr' if lang == 'en' else 'rtl'


def health(request):
    return HttpResponse("ok", content_type="text/plain")


def homepage(request):
    lang = _lang(request)
    site_url = getattr(settings, 'SITE_URL', 'http://localhost:8000').rstrip('/')
    return render(request, 'reader.html', {
        'lang': lang,
        'direction': _dir(lang),
        'component': json.dumps('LibraryHome'),
        'props': json.dumps({'lang': lang}),
        'page_title': 'TzuratLink – Talmud Library',
        'page_description': 'Browse the Babylonian Talmud with linked commentaries on TzuratLink',
        'page_image': '',
        'canonical_url': f'{site_url}/',
        'structured_data': json.dumps({
            '@context': 'https://schema.org',
            '@type': 'WebSite',
            'name': 'TzuratLink',
            'url': f'{site_url}/',
        }),
        'ref': '',
    })


def dafyomi_redirect(request):
    if request.method != 'GET':
        return JsonResponse({'error': "You are not permitted"}, status=403)
    try:
        req = urllib.request.Request('https://www.sefaria.org/api/calendars')
        with urllib.request.urlopen(req, timeout=5) as response:
            data = response.read()
            json_data = json.loads(data.decode(response.headers.get_content_charset('utf-8')))
        for item in json_data.get('calendar_items', []):
            if item.get('title', {}).get('en') == 'Daf Yomi':
                return redirect('page_view', ref=item['ref'] + 'a')
        return JsonResponse({'error': "Daf Yomi not found"}, status=404)
    except urllib.error.URLError:
        return JsonResponse({'error': "Failed to fetch Daf Yomi reference"}, status=503)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def page_view(request, ref):
    if request.method != 'GET':
        return JsonResponse({'error': "You are not permitted"}, status=403)
    lang = _lang(request)
    page_data = get_for_sref(ref)
    if page_data is None:
        return JsonResponse({'error': "Page not found"}, status=404)
    site_url = getattr(settings, 'SITE_URL', 'http://localhost:8000').rstrip('/')
    title = f"{ref} | TzuratLink"
    seo_text = get_sefaria_seo_text(page_data.get('sefaria_ref') or ref)
    return render(request, 'reader.html', {
        'lang': lang,
        'direction': _dir(lang),
        'component': json.dumps('PDFReader'),
        'props': json.dumps({**page_data, 'lang': lang}),
        'page_title': title,
        'page_description': f"Study {ref} with linked commentaries on TzuratLink",
        'page_image': '',
        'canonical_url': f'{site_url}/page/{ref}',
        'structured_data': json.dumps({
            '@context': 'https://schema.org',
            '@type': 'ScholarlyArticle',
            'headline': title,
            'url': f'{site_url}/page/{ref}',
        }),
        'ref': ref,
        'seo_text': seo_text,
    })


def tractate_view(request, name):
    lang = _lang(request)
    site_url = getattr(settings, 'SITE_URL', 'http://localhost:8000').rstrip('/')
    return render(request, 'reader.html', {
        'lang': lang,
        'direction': _dir(lang),
        'component': json.dumps('TractateView'),
        'props': json.dumps({'tractate': name}),
        'page_title': f'{name} | TzuratLink',
        'page_description': f'Study tractate {name} on TzuratLink',
        'page_image': '',
        'canonical_url': f'{site_url}/tractate/{name}',
        'structured_data': json.dumps({'@context': 'https://schema.org', '@type': 'WebPage', 'name': name}),
        'ref': '',
    })


def tractate_api(request, name):
    if request.method != 'GET':
        return JsonResponse({'error': "Method not allowed"}, status=405)
    from core.models import Page
    import re as _re
    try:
        pattern = _re.compile(rf'^{_re.escape(name)}\s+(\d+)([ab])$')
        amudim = []
        for page in Page.objects(ref=_re.compile(rf'^{_re.escape(name)} \d+[ab]$')).only('ref'):
            m = pattern.match(page.ref)
            if m:
                amudim.append({'ref': page.ref, 'daf': int(m.group(1)), 'side': m.group(2)})
        amudim.sort(key=lambda x: (x['daf'], x['side']))
        return JsonResponse({'tractate': name, 'amudim': amudim})
    except Exception as e:
        return JsonResponse({'tractate': name, 'amudim': [], 'error': str(e)})



def render_page(request, ref):
    """Return a cropped PNG of the page rendered server-side via PyMuPDF."""
    if request.method != 'GET':
        return JsonResponse({'error': "Method not allowed"}, status=405)
    from core.models import Page
    from core.render import render_page_png
    try:
        page = Page.objects(ref=ref).first()
        if not page:
            return JsonResponse({'error': 'not found'}, status=404)
        png = render_page_png(page)
        resp = HttpResponse(png, content_type='image/png')
        resp['Cache-Control'] = 'public, max-age=86400'
        return resp
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def reader_catchall(request, path=''):
    return redirect('homepage')


def get_page_data(request, ref):
    if request.method != 'GET':
        return JsonResponse({'error': "Method not allowed"}, status=405)
    page_data = get_for_sref(ref)
    if page_data is None:
        return JsonResponse({'error': "Page not found"}, status=404)
    return JsonResponse(page_data)


def library_api(request):
    if request.method != 'GET':
        return JsonResponse({'error': "Method not allowed"}, status=405)
    from core.models import Page
    try:
        tractates = {}
        pattern = re_module.compile(r'^(.+?)\s+\d+[ab]$')
        for page in Page.objects.only('ref'):
            if not page.ref:
                continue
            m = pattern.match(page.ref)
            if m:
                name = m.group(1)
                if name not in tractates or page.ref < tractates[name]:
                    tractates[name] = page.ref
        return JsonResponse({'available': list(tractates.keys()), 'first_refs': tractates})
    except Exception as e:
        return JsonResponse({'available': [], 'first_refs': {}, 'error': str(e)})


def get_next_page(request, ref):
    if request.method != 'GET':
        return JsonResponse({'error': "Method not allowed"}, status=405)
    try:
        if ref.endswith('a'):
            next_ref = ref[:-1] + 'b'
            return JsonResponse({'ref': next_ref, 'exists': get_for_sref(next_ref) is not None})
        return JsonResponse({'ref': None, 'exists': False})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def get_prev_page(request, ref):
    if request.method != 'GET':
        return JsonResponse({'error': "Method not allowed"}, status=405)
    try:
        if ref.endswith('b'):
            prev_ref = ref[:-1] + 'a'
            return JsonResponse({'ref': prev_ref, 'exists': get_for_sref(prev_ref) is not None})
        return JsonResponse({'ref': None, 'exists': False})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def debug_page(request, ref):
    from core.models import Page
    try:
        page = Page.objects(ref=ref).first()
        if not page:
            return JsonResponse({'error': 'not found', 'ref': ref})
        return JsonResponse({
            'ref': page.ref,
            'sefaria_ref': page.effective_sefaria_ref(),
            'source_pdf': page.source_pdf,
            'bbox_count': len(page.bboxes or []),
            'id': str(page.id),
        })
    except Exception as e:
        return JsonResponse({'error': str(e)})
