from django.urls import path
from . import views
from django.views.decorators.http import require_POST

urlpatterns = [
    path('', views.dashboard, name='admin_dashboard'),
    
    path('bao-cao/', views.danh_sach_bao_cao, name='admin_bao_cao'), 
    path('yeu-cau-xoa/', views.removal_requests, name='admin_yeu_cau_xoa'),
    
    path('xu-ly-xoa/<int:notification_id>/', views.xu_ly_yeu_cau_xoa, name='xu_ly_yeu_cau_xoa'),
    
    path('thanh-vien/', views.quan_ly_thanh_vien, name='quan_ly_thanh_vien'),
    path('quan-ly-truyen/', views.quan_ly_truyen, name='admin_quan_ly_truyen'),

    path('quan-ly-truyen/xoa/<slug:slug>/', views.admin_xoa_truyen, name='admin-xoa-truyen'),

    path('api-gui-bao-cao/<int:truyen_id>/', views.api_gui_bao_cao, name='api-gui-bao-cao'),
    path('xu-ly-bao-cao/<int:report_id>/', views.xu_ly_bao_cao_admin, name='admin-xu-ly-bao-cao'),

    path('thanh-vien/quyen/<int:user_id>/', views.thay_doi_quyen_admin, name='admin_change_role'),
    path('thanh-vien/xoa/<int:user_id>/', views.xoa_thanh_vien, name='admin_xoa_user'),

    path('the-loai/', views.quan_ly_the_loai, name='admin_the_loai'),
    path('the-loai/xoa/<int:genre_id>/', views.xoa_the_loai, name='admin_xoa_the_loai'),
]