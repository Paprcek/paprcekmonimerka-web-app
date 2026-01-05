from django.urls import path
from . import views

urlpatterns = [
    path('', views.tictactoe_game, name='tictactoe'),
    path('move/', views.ai_move, name='ai_move'),
    path('update-record/', views.update_tictactoe_record, name='update_tictactoe_record'),
]