# tictactoe/urls.py

from django.urls import path
from . import views

urlpatterns = [
    # Cesta pro zobrazení hry (načtení aktivní hry nebo začátek nové)
    path('tictactoe/', views.tictactoe_game, name='tictactoe_game'),

    # Cesta pro PŘIJETÍ TAHU (API endpoint volaný přes JS/fetch)
    # Potřebuje ID hry (int) jako parametr
    path('tictactoe/move/<int:game_id>/', views.make_move, name='make_move'),
    
    # Cesta pro ZAČÁTEK NOVÉ HRY
    path('tictactoe/new/', views.new_game, name='new_game'),
]
