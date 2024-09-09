from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.middleware.csrf import get_token

# Temporary function for development
@ensure_csrf_cookie
def get_csrf_token(request):
    return JsonResponse({'csrfToken': get_token(request)})

def mask_username(username):
    if len(username) == 2:
        return username[0] + '*'
    elif len(username) == 3:
        return username[0:2] + '*'
    elif len(username) == 4:
        return username[0:3] + '*'
    else:
        return username[0:4] + '*' * (len(username) - 4)