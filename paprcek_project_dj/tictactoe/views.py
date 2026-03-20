import json
from .models import TicTacToeRecord
from django.views.decorators.csrf import ensure_csrf_cookie
from django.shortcuts import render
from django.http import JsonResponse

def update_tictactoe_record(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            new_time = data.get('time')
            
            if new_time is not None:
                TicTacToeRecord.objects.create(time_seconds=int(new_time))
                best_record = TicTacToeRecord.objects.order_by('time_seconds').first()
                
                return JsonResponse({
                    'status': 'success',
                    'world_best': best_record.time_seconds if best_record else None
                })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
            
    return JsonResponse({'status': 'error'}, status=400)

def tictactoe_game(request):
    best_record = TicTacToeRecord.objects.order_by('time_seconds').first()
    context = {
        'world_best': best_record.time_seconds if best_record else None
    }
    return render(request, 'tictactoe/tictactoe_game.html', context)

import random

def get_score(board, x, y, symbol, opponent_symbol):
    """Vypočítá atraktivitu políčka pro daný symbol (útok i obranu)."""
    score = 0
    directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
    
    for dx, dy in directions:
        count = 1
        for i in range(1, 5):
            nx, ny = x + i*dx, y + i*dy
            if 0 <= nx < 15 and 0 <= ny < 15 and board[ny][nx] == symbol:
                count += 1
            else: break
        for i in range(1, 5):
            nx, ny = x - i*dx, y - i*dy
            if 0 <= nx < 15 and 0 <= ny < 15 and board[ny][nx] == symbol:
                count += 1
            else: break
            
        if count >= 5: score += 100000 
        elif count == 4: score += 5000
        elif count == 3: score += 500
        elif count == 2: score += 50
    return score

def ai_move(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        board = data.get('board')
        last_x = data.get('x')
        last_y = data.get('y')

        if check_winner(board, last_x, last_y, 'X'):
            return JsonResponse({'status': 'win', 'winner': 'player'})

        best_score = -1
        best_move = None
        
        # Optimization: only consider moves adjacent to existing pieces
        # (reduces computation and avoids evaluating empty board areas) 
        # (aby nezkoumala prázdné rohy mapy a byla rychlejší)
        for y in range(15):
            for x in range(15):
                if board[y][x] == "":
                    has_neighbor = False
                    for dy in range(-1, 2):
                        for dx in range(-1, 2):
                            ny, nx = y + dy, x + dx
                            if 0 <= ny < 15 and 0 <= nx < 15 and board[ny][nx] != "":
                                has_neighbor = True
                                break
                        if has_neighbor: break
                    
                    if has_neighbor:
                        attack_score = get_score(board, x, y, "O", "X")
                        defense_score = get_score(board, x, y, "X", "O")
                        
                        # Defense is prioritized by weighting it 1.2x
                        total_score = attack_score + (defense_score * 1.2)
                        total_score += random.random()

                        if total_score > best_score:
                            best_score = total_score
                            best_move = (x, y)

        if best_move is None:
            ai_x, ai_y = 7, 7
        else:
            ai_x, ai_y = best_move

        board[ai_y][ai_x] = 'O'
        if check_winner(board, ai_x, ai_y, 'O'):
            return JsonResponse({
                'status': 'win', 
                'winner': 'ai', 
                'ai_x': ai_x, 
                'ai_y': ai_y
            })

        return JsonResponse({
            'status': 'success',
            'ai_x': ai_x,
            'ai_y': ai_y
        })

def check_winner(board, x, y, symbol):
    """Zkontroluje, zda po tahu na [x, y] nevznikla řada 5 symbolů."""
    directions = [
        (1, 0),
        (0, 1),
        (1, 1),
        (1, -1)
    ]
    
    board_size = 15

    for dx, dy in directions:
        count = 1
        for i in range(1, 5):
            nx, ny = x + i*dx, y + i*dy
            if 0 <= nx < board_size and 0 <= ny < board_size and board[ny][nx] == symbol:
                count += 1
            else:
                break
        for i in range(1, 5):
            nx, ny = x - i*dx, y - i*dy
            if 0 <= nx < board_size and 0 <= ny < board_size and board[ny][nx] == symbol:
                count += 1
            else:
                break
        
        if count >= 5:
            return True
    return False