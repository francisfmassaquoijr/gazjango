from django.conf import settings

def api_keys(request):
    return { 'FACEBOOK_API_KEY': settings.FACEBOOK_LOGIN_API_KEY }
