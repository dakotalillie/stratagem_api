from django.urls import path, include
from rest_framework.authtoken import views as rest_framework_views

from . import views

urlpatterns = [
    path('login/', rest_framework_views.obtain_auth_token),
    path('games/', views.GamesList.as_view()),
    path('games/<uuid:pk>/', views.GamesDetail.as_view()),
    path('games/<uuid:pk>/orders', views.OrdersList.as_view())
]
