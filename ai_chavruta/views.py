import json

from django.http import JsonResponse, StreamingHttpResponse

from .services.chat_service import ChatRequest, ChavrutaChatService

_chat_service = ChavrutaChatService()


def chat(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    # daf_ref/question validation is the graph's job (validate_request node)
    # so every failure mode — missing fields, a malformed daf_ref, an LLM
    # outage — surfaces through the same event stream, rather than the
    # frontend having to handle a separate error format.
    chat_request = ChatRequest(
        user_id=request.user.id,
        daf_ref=(data.get('daf_ref') or '').strip(),
        question=(data.get('question') or '').strip(),
        session_id=data.get('session_id') or None,
        explicit_mode=data.get('mode') or None,
    )

    def event_stream():
        for event in _chat_service.stream(chat_request):
            yield json.dumps(event) + "\n"

    response = StreamingHttpResponse(event_stream(), content_type='application/x-ndjson')
    response['Cache-Control'] = 'no-cache'
    response['X-Accel-Buffering'] = 'no'  # don't let a reverse proxy buffer this away
    return response
