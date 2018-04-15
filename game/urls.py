from django.urls import path, include
from rest_framework_jwt.views import obtain_jwt_token
from . import views

urlpatterns = [
    path('login/', obtain_jwt_token),
    path('current_user/', views.current_user),
    path('users/', views.UserList.as_view()),
    path('games/', views.GameList.as_view()),
    path('games/sandbox/', views.Sandbox.as_view()),
    path('games/<uuid:pk>/', views.GameDetail.as_view()),
    path('games/<uuid:pk>/orders', views.OrderList.as_view())
]
