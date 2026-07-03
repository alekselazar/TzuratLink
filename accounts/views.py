import json
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.http import JsonResponse
from core.backup import backup_async

User = get_user_model()


def me(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Not authenticated'}, status=401)
    return JsonResponse({
        'id': request.user.id,
        'email': request.user.email,
        'name': request.user.get_full_name() or request.user.email,
    })


def signup_view(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    try:
        data = json.loads(request.body)
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        name = data.get('name', '').strip()

        if not email or not password:
            return JsonResponse({'error': 'Email and password are required'}, status=400)
        if len(password) < 8:
            return JsonResponse({'error': 'Password must be at least 8 characters'}, status=400)
        if User.objects.filter(email=email).exists():
            return JsonResponse({'error': 'Email already registered'}, status=400)

        user = User.objects.create_user(username=email, email=email, password=password)
        if name:
            parts = name.split(' ', 1)
            user.first_name = parts[0]
            user.last_name = parts[1] if len(parts) > 1 else ''
            user.save(update_fields=['first_name', 'last_name'])

        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        backup_async()
        return JsonResponse({
            'id': user.id,
            'email': user.email,
            'name': user.get_full_name() or user.email,
        })
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def login_view(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    try:
        data = json.loads(request.body)
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')

        user = authenticate(request, username=email, password=password)
        if user is None:
            return JsonResponse({'error': 'Invalid email or password'}, status=401)

        login(request, user)
        return JsonResponse({
            'id': user.id,
            'email': user.email,
            'name': user.get_full_name() or user.email,
        })
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def logout_view(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    logout(request)
    return JsonResponse({'ok': True})
