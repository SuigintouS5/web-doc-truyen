from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='admin_dashboard'),
    path('bao-cao/', views.danh_sach_bao_cao, name='admin_bao_cao'),
    path('yeu-cau-xoa/', views.removal_requests, name='admin_yeu_cau_xoa'),
    
    # Thêm cái này vào ĐÂY nếu bạn muốn nút bấm gửi về link admin
    path('api-gui-bao-cao/<int:truyen_id>/', views.gui_bao_cao_api, name='api_gui_bao_cao'),
]