from django.urls import path
from . import views

app_name = 'logic'

urlpatterns = [
    path('', views.logic_game, name='logic'),
    path('save-score/', views.save_score, name='save_score'),
]