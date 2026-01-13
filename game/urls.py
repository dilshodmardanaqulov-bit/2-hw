from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('start/', views.start_game, name='start_game'),
    path('play/', views.play, name='play'),
    path('attack/', views.attack, name='attack'),
    path('move/', views.move, name='move'),
path('play/', views.play, name='play'),
    path('heal/', views.heal, name='heal'),
    path('game-over/', views.game_over, name='game_over'),
    path('victory/', views.victory, name='victory'),
]
