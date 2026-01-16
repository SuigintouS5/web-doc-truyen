from django.urls import path
from . import views

urlpatterns = [
    path('', views.truyen_list, name='truyen-list'),
    path('truyen/<slug:slug>/', views.truyen_detail, name='truyen-detail'),
    path('the-loai/<slug:slug>/', views.genre_detail, name='genre-detail'),
]
