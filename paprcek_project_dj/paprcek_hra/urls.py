from django.contrib import admin
from django.urls import path, include
from django.views.i18n import JavaScriptCatalog
from . import views
 

urlpatterns = [
    path('jsi18n/', JavaScriptCatalog.as_view(), name='javascript-catalog'),
    path('admin/', admin.site.urls),
    path('set-language/', views.set_language_custom, name='set_language'),
    path('game/', views.game_hub, name='game_hub'),
    path('game/tictactoe/', include('tictactoe.urls', namespace='tictactoe')),
    path('game/logic/', include('logic.urls', namespace='logic')),
    path('', views.game_hub, name='home'),
]