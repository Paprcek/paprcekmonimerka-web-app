from django.shortcuts import render, redirect
from django.utils import translation
from django.conf import settings

def game_hub(request):
    return render(request, 'hub.html')

def set_language_custom(request):
    print("!!! POŽADAVEK NA ZMĚNU JAZYKA DORAZIL DO DJANGA !!!")
    lang_code = request.POST.get('language') or request.GET.get('language')
    next_url = request.POST.get('next', '/')
    
    print(f"DEBUG: Jazyk: {lang_code}, Návratová URL: {next_url}")
    
    if lang_code and lang_code in dict(settings.LANGUAGES):
        translation.activate(lang_code)
        response = redirect(next_url)
        response.set_cookie(settings.LANGUAGE_COOKIE_NAME, lang_code)
        return response
    return redirect(next_url)