import json

from django.http import JsonResponse

from .services.chat_service import ChatRequest, ChavrutaChatService

_chat_service = ChavrutaChatService()


def chat(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    # daf_ref/question validation is the graph's job (validate_request node)
    # so every failure mode — missing fields, a malformed daf_ref, an LLM
    # outage — surfaces through the same {"answer": "..."} shape, rather
    # than the frontend having to handle two different error formats.
    chat_request = ChatRequest(
        user_id=request.user.id if request.user.is_authenticated else None,
        daf_ref=(data.get('daf_ref') or '').strip(),
        question=(data.get('question') or '').strip(),
        session_id=data.get('session_id') or None,
        explicit_mode=data.get('mode') or None,
    )

    result = _chat_service.invoke(chat_request)
    return JsonResponse(result)
