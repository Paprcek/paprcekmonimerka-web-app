from django.shortcuts import render, redirect
from django.utils import translation
from django.conf import settings

def game_hub(request):
    return render(request, 'hub.html')

def set_language_custom(request):
    lang_code = request.POST.get('language') or request.GET.get('language')
    next_url = request.POST.get('next', '/')
    
    print(f"DEBUG: Jazyk: {lang_code}, Návratová URL: {next_url}")
    
    if lang_code and lang_code in dict(settings.LANGUAGES):
        translation.activate(lang_code)
        response = redirect(next_url)
        
        # Nastavení cookie s parametry pro moderní prohlížeče
        response.set_cookie(
            settings.LANGUAGE_COOKIE_NAME, 
            lang_code,
            max_age=365*24*60*60,  # 1 rok
            path='/',              # Důležité: platnost pro celý web
            secure=True,           # Nutné pro HTTPS (Cloudflare)
            samesite='Lax'         # Standard pro bezpečnost
        )
        print(f"DEBUG: Cookie {settings.LANGUAGE_COOKIE_NAME} nastavena na {lang_code}")
        return response
    
    print("DEBUG: Jazyk nebyl rozpoznán nebo není v settings.LANGUAGES")
    return redirect(next_url)

def tictactoe_view(request):
# Zatím jen vrátí jednoduchý text, dokud hru nedoděláš
    from django.http import HttpResponse
    return HttpResponse("Tady se připravují piškvorky!")