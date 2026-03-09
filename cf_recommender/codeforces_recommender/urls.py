from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('api/user/<str:handle>/', views.user_info, name='user_info'),
    path('api/recommend/<str:handle>/', views.recommend_problems_view, name='recommend_problems'),
]