from django.http import HttpResponse

def index(request):
    return HttpResponse("Django Routing funguje! Vítej na /game/.")
