from django.urls import path
from . import views

urlpatterns = [
    # URL: /admin-tong/
    path('', views.dashboard, name='admin_dashboard'),
    
    # URL: /admin-tong/bao-cao/ (Bỏ chữ admin-tong/ ở đây)
    path('bao-cao/', views.danh_sach_bao_cao, name='admin_bao_cao'),
    
    # URL: /admin-tong/yeu-cau-xoa/
    path('yeu-cau-xoa/', views.removal_requests, name='admin_yeu_cau_xoa'),
]