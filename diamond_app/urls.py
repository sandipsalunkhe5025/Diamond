from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('download/<str:filename>/', views.download_output, name='download_output'),
]