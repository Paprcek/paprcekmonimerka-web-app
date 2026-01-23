import json
from django.http import JsonResponse
from .models import LogicScore
from django.shortcuts import render
from django.http import HttpResponse

def save_score(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            LogicScore.objects.create(
                player_name="Hráč", 
                time=data['time'],
                difficulty=data.get('difficulty', 'normal')
            )
            return JsonResponse({"status": "ok"})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=400)

def logic_game(request):
    best_normal = LogicScore.objects.filter(difficulty='normal').order_by('time').first()
    best_hard = LogicScore.objects.filter(difficulty='hard').order_by('time').first()
    
    context = {
        'best_time_normal': best_normal.time if best_normal else "--.--",
        'best_time_hard': best_hard.time if best_hard else "--.--"
    }
    return render(request, 'logic/logic_game.html', context)