from django.utils.timezone import now
from django.contrib.auth import logout
from root import settings
from django.shortcuts import redirect

class AutoLogOutMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            last_activity = request.session.get('last_activity')
            if last_activity:
                difference = (now() - now().fromisoformat(last_activity)).total_seconds()
                if difference > settings.SESSION_COOKIE_AGE:
                    logout(request)
                    return redirect('ecommerce:index')
            request.session['last_activity'] = now().isoformat()

        response = self.get_response(request)
        return response
