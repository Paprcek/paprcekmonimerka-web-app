from django.urls import path

from . import views

app_name = 'czu'

urlpatterns = [
    path('', views.index, name='index'),
    path('assets/<str:name>', views.asset, name='asset'),
    path('<slug:slug>/', views.subject, name='subject'),
    path('<slug:slug>/nahodny/', views.random_test, name='random'),
    path('<slug:slug>/test/<int:seed>/', views.test, name='test'),
]
