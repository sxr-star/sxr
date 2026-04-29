from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('register_with_info/', views.register_with_info, name='register_with_info'),
]
