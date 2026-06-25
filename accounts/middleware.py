"""Session Timeout Middleware — enforces inactivity timeout."""

from django.contrib.auth import logout
from django.utils import timezone
from django.conf import settings
from django.shortcuts import redirect


class SessionTimeoutMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.timeout = getattr(settings, 'SESSION_COOKIE_AGE', 300)

    def __call__(self, request):
        if request.user.is_authenticated:
            last_activity = request.session.get('last_activity')
            now = timezone.now().timestamp()

            if last_activity:
                elapsed = now - last_activity
                if elapsed > self.timeout:
                    logout(request)
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        from django.http import JsonResponse
                        return JsonResponse({'error': 'Session expired', 'redirect': '/accounts/login/'}, status=401)
                    return redirect('/accounts/login/?timeout=1')

            request.session['last_activity'] = now

        response = self.get_response(request)
        return response
