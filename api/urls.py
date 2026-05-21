from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('register_with_info/', views.register_with_info, name='register_with_info'),
    path('register_with_info_v3/', views.register_with_info_v3, name='register_with_info_v3'),
    path('send_code/', views.send_code, name='send_code'),
    path('verify_code/', views.verify_code, name='verify_code'),
    path('check_login/', views.check_login, name='check_login'),
    path('logout/', views.logout, name='logout'),
    # 4.0新增接口
    path('review_status/', views.review_status, name='review_status'),
    path('admin_review/', views.admin_review, name='admin_review'),
    path('admin_statistics/', views.admin_statistics, name='admin_statistics'),
]
