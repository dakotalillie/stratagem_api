from django.urls import path

from . import views

urlpatterns = [
    path('games/', views.GamesList.as_view()),
    path('games/<uuid:pk>/', views.GamesDetail.as_view()),
    path('games/<uuid:pk>/orders', views.OrdersList.as_view())
]
