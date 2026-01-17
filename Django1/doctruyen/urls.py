from django.urls import path
from . import views

urlpatterns = [
    path('', views.truyen_list, name='truyen-list'),
    path('truyen/<slug:slug>/', views.truyen_detail, name='truyen-detail'),
    path('truyen/<slug:slug>/edit/', views.truyen_edit, name='truyen-edit'),
    path('the-loai/<slug:slug>/', views.genre_detail, name='genre-detail'),

    # AUTH
    path("dang-nhap/", views.login_view, name="user-login"),
    path("dang-ky/", views.register_view, name="user-register"),
    path("dang-xuat/", views.logout_view, name="logout"),
]
