import json
from django.http import JsonResponse
from .models import LogicScore
from django.shortcuts import render
from django.http import HttpResponse

def save_score(request):
    if request.method == "POST":
        data = json.loads(request.body)
        LogicScore.objects.create(
            player_name="Hráč", 
            time=data['time']
        )
        return JsonResponse({"status": "ok"})

def logic_game(request):
    best_score = LogicScore.objects.order_by('time').first()
    
    context = {
        'best_time': best_score.time if best_score else "--.--"
    }
    return render(request, 'logic/logic_game.html', context)