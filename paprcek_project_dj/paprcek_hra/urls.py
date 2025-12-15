
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.i18n import i18n_patterns

urlpatterns = [
    path('admin/', admin.site.urls),
    
    path('i18n/', include('django.conf.urls.i18n')),
    
    path('game/', include('tictactoe.urls')),
]
