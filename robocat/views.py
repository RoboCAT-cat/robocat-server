from django.shortcuts import redirect
from django.templatetags.static import static

def favicon_redirect(request):
    return redirect(static('favicon.ico'), permanent=True)
