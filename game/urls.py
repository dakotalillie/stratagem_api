from django.urls import path, include
from rest_framework.authtoken import views as drf_views

from . import views

urlpatterns = [
    path('login/', drf_views.obtain_auth_token),
    path('current_user/', views.Sessions.as_view()),
    path('games/', views.GamesList.as_view()),
    path('games/<uuid:pk>/', views.GamesDetail.as_view()),
    path('games/<uuid:pk>/orders', views.OrdersList.as_view())
]
