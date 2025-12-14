from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseBadRequest
from .models import GameState  
import json
import random # Pro AI

# --- 1. Logika Vítěze ---
def check_winner(board_str):
    winning_combinations = [
        (0, 1, 2), (3, 4, 5), (6, 7, 8),  # Řádky
        (0, 3, 6), (1, 4, 7), (2, 5, 8),  # Sloupce
        (0, 4, 8), (2, 4, 6)              # Diagonály
    ]
    for combo in winning_combinations:
        a, b, c = combo
        if board_str[a] != '.' and board_str[a] == board_str[b] and board_str[a] == board_str[c]:
            return board_str[a]

    if '.' not in board_str:
        return 'Draw'

    return None

# --- 2. Logika AI (Náhodný tah) ---
def get_ai_move(board_str):
    empty_cells = [i for i, char in enumerate(board_str) if char == '.']
    if empty_cells:
        return random.choice(empty_cells)
    return None

# --- View pro Zobrazení a Načtení Poslední Hry ---
def tictactoe_game(request):
    try:
        # Najde poslední hru, která není ukončená
        game = GameState.objects.filter(status='Active').latest('updated_at')
    except GameState.DoesNotExist:
        # Pokud aktivní hra neexistuje, vytvoříme novou
        game = GameState.objects.create()

    context = {
        'game': game,
        'current_player': 'X' if game.is_x_turn else 'O',
    }
    return render(request, 'tictactoe/tictactoe_game.html', context)

# --- View pro Zpracování Tahu hráče a AI (API ENDPOINT) ---
def make_move(request, game_id):
    if request.method != 'POST':
        return HttpResponseBadRequest("Očekáván POST požadavek.")

    game = get_object_or_404(GameState, pk=game_id)
    # ZDE KONTROLA: Hráč smí táhnout jen tehdy, když je status 'Active' a je řada X
    if game.status != 'Active' or not game.is_x_turn:
        return JsonResponse({'error': 'Není tvůj tah nebo hra skončila.'}, status=400)

    # Zpracování dat z frontendu (index pole)
    try:
        data = json.loads(request.body)
        index = int(data.get('index'))
    except Exception:
        return HttpResponseBadRequest("Neplatný formát dat.")

    current_board = list(game.board)

    # 1. Tah hráče 'X'
    if index >= 0 and index <= 8 and current_board[index] == '.':
        current_board[index] = 'X'
        game.board = "".join(current_board)
        game.is_x_turn = False # Nyní hraje AI

        ai_index = None # Inicializace

        # 2. Test vítěze po tahu hráče 'X'
        winner = check_winner(game.board)
        if winner:
            game.status = f'{winner}_Wins' if winner != 'Draw' else 'Draw'

        # 3. Tah AI ('O'), pokud hra pokračuje
        if game.status == 'Active':
            ai_index = get_ai_move(game.board)
            if ai_index is not None:
                current_board[ai_index] = 'O'
                game.board = "".join(current_board)
                game.is_x_turn = True # Tah se vrací na Člověka ('X')

                # 4. Test vítěze po tahu AI 'O'
                winner = check_winner(game.board)
                if winner:
                    game.status = f'{winner}_Wins' if winner != 'Draw' else 'Draw'
            else:
                # Nastane, pokud by deska byla plná po tahu X (měla by být detekována už výše)
                game.status = 'Draw' 

        game.save()

        # 5. Odpověď pro frontend
        return JsonResponse({
            'board': game.board,
            'status': game.status,
            'winner': winner,
            'ai_move_index': ai_index # Vrátíme, kam AI táhla
        })

    return JsonResponse({'error': 'Neplatný tah hráče X.'}, status=400)

# View pro spuštění nové hry
def new_game(request):
    GameState.objects.create(board='.........', is_x_turn=True, status='Active')
    return redirect('tictactoe_game')

# Původní game_index view
def game_index(request):
    return render(request, 'tictactoe/index.html', {})
