from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse

import json

from core.utils import get_incompleted_page, get_unreviewed_page, create_new_page, complete, review, save_sent, get_untranslated_sentance, save_translations, get_lines

@login_required
def index(request):
    if not request.user.is_staff:
        return JsonResponse({'error': "You are not permitted"}, status=403)
    
    if request.method == 'POST':
        try:
            body = json.loads(request.body)
            url = body['fileUrl']
            anchors = body['anchors']
            create_new_page(url, anchors)
            return JsonResponse({'success': 'Page successfuly initialized in database'})
        except:
            return JsonResponse({'error': 'Bad data'}, status=400)
        
    unreviewed = None
    
    if request.user.is_superuser:
        unreviewed = get_unreviewed_page()
    incompleted = get_incompleted_page()
    untranslated = get_untranslated_sentance()

    if incompleted:
        return render(request,
                      'editor.html',
                      context={
                          'app': 'EditorApp',
                          'component': 'PDFEditor',
                          'props': json.dumps(incompleted)
                          })
    if unreviewed:
        return render(request,
                      'editor.html',
                      context={
                          'app': 'EditorApp',
                          'component': 'PDFReviewer',
                          'props': json.dumps(unreviewed)
                          })
    if untranslated:
        #translations = get_openai_translations(untranslated.pk)
        return render(request,
                      'editor.html',
                      context={
                          'app': 'EditorApp',
                          'component': 'TranslationsEditor',
                          'props': json.dumps({
                              'sentanceId': untranslated.pk,
                              'sentance': untranslated.sentance
                              })
                          })
        
    
    return render(request, 'editor.html', context={'app': 'EditorApp',
                                                   'component': 'EditorInput',
                                                   'props': '{}'})

@login_required
def lines(request, page_id):
    if not request.user.is_staff:
        return JsonResponse({'error': "You are not permitted"}, status=403)
    lines = get_lines(page_id)
    if lines:
        return JsonResponse(lines, status=200)
    return JsonResponse({'error': 'Data for requested page not found'}, status=404)

@login_required
def save_sentance(request):
    if not request.user.is_staff:
        return JsonResponse({'error': "You are not permitted"}, status=403)
    if not request.method == 'POST':
        return JsonResponse({'error': "Bad request"}, status=405)
    try:
        body = json.loads(request.body)
        page_id = body['page_id']
        sefaria_ref = body['sefaria_ref']
        related_text = body['related_text']
        boxes = body['boxes']
        to_translate = body['to_translate']
        saved = save_sent(page_id, sefaria_ref, related_text, boxes, to_translate)
        if saved:
            return JsonResponse({'success': 'Sentance saved'}, status=200)
    except:
        return JsonResponse({'error': 'Bad request'}, status=400)
    return JsonResponse({'error': 'Bad response'}, status=400)

@login_required
def complete_page(request):
    if not request.user.is_staff:
        return JsonResponse({'error': "You are not permitted"}, status=403)
    if not request.method == 'POST':
        return JsonResponse({'error': "Bad request"}, status=405)
    try:
        body = json.loads(request.body)
        page_id = body['page_id']
        completed = complete(page_id)
        if completed:
            return JsonResponse({'success': 'Page completed'}, status=200)
    except:
        return JsonResponse({'error': 'Bad request'}, status=400)
    return JsonResponse({'error': 'Bad response'}, status=400)

@login_required
def review_page(request):
    if not request.user.is_superuser:
        return JsonResponse({'error': "You are not permitted"}, status=403)
    if not request.method == 'POST':
        return JsonResponse({'error': "Bad request"}, status=405)
    try:
        body = json.loads(request.body)
        page_id = body['page_id']
        reviewed = review(page_id)
        if reviewed:
            return JsonResponse({'success': 'Page reviewed'}, status=200)
    except:
        return JsonResponse({'error': 'Bad request'}, status=400)
    return JsonResponse({'error': 'Bad response'}, status=400)

@login_required
def translates(request):
    if not request.user.is_staff:
        return JsonResponse({'error': "You are not permitted"}, status=403)
    if request.method == 'POST':
        try:
            body = json.loads(request.body)
            success_pk = save_translations(body)
            if success_pk:
                return JsonResponse({'success': 'Translations saved'})
        except:
            return JsonResponse({'error': 'Bad request'}, status=400)
    return JsonResponse({'error': 'Bad response'}, status=400)