from django.urls import path, include

from . import views

urlpatterns = [
    path('login/', views.Login.as_view()),
    path('games/', views.GamesList.as_view()),
    path('games/<uuid:pk>/', views.GamesDetail.as_view()),
    path('games/<uuid:pk>/orders', views.OrdersList.as_view())
]
