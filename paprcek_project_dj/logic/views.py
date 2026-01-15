from django.shortcuts import render
from django.http import HttpResponse

def logic_view(request):
    return HttpResponse("Tady se připravuje Logic!")

