from django.urls import path
from . import views

urlpatterns = [
    path('', views.tictactoe_game, name='tictactoe_game'),
]