from django.urls import path
from . import views

urlpatterns = [
    # Jméno 'Logic' musí odpovídat tomu, co voláš v HTML šabloně
    path('', views.logic_view, name='logic'),
]