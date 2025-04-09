from django.shortcuts import render, redirect
from django.http import JsonResponse
import json
import urllib.request
from core.utils import get_for_sref

def index(request):
    redirect('daf_yomi')

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
    
    page_data = get_for_sref(ref)

    return render(request,
                'dafyomi.html',
                context={
                    'amud': amud,
                    'component': json.dumps('PDFReader'),
                    'props': json.dumps(page_data)
                    })
