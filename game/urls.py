from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.GameList.as_view()),
    path('sandbox/', views.Sandbox.as_view()),
    path('<uuid:pk>/', views.GameDetail.as_view()),
    path('<uuid:pk>/orders', views.OrderList.as_view())
]
