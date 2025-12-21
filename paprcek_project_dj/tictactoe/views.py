from django.shortcuts import render
from django.http import HttpResponse

def tictactoe_game(request):
    return render(request, 'tictactoe/tictactoe_game.html', {})