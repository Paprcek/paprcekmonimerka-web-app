from django.contrib import admin
from django.urls import path, include
from . import views
 

urlpatterns = [
    path('admin/', admin.site.urls),
    path('set-language/', views.set_language_custom, name='set_language'),
    path('game/', views.game_hub, name='game_hub'),
    path('game/tictactoe/', include('tictactoe.urls')),
    path('', views.game_hub, name='home'),
]