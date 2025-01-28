from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse

import json

from core.utils import get_incompleted_page, get_unreviewed_page, create_new_page, complete, review, save_sent, get_untranslated_sentance, save_translations, get_openai_translations

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

    if incompleted or untranslated:
        return render(request,
                      'editor.html',
                      context={
                          'component': json.dumps('EditorTaskManager'),
                          'props': {
                              'inincompleted': json.dumps(incompleted),
                              'unreviewed': json.dumps(unreviewed),
                              'untranslated': json.dumps(untranslated)
                              }
                            })
    
    return render(request, 'editor.html', context={'component': json.dumps('EditorInput')})

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
        saved = save_sent(page_id, sefaria_ref, related_text, boxes)
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

    sentance_id = get_untranslated_sentance().pk    
    translations = get_openai_translations(sentance_id)
    if translations:
        return JsonResponse(translations, staus=200)
    return JsonResponse({'error': 'Bad response'}, status=400)