from django.urls import path
from . import views

urlpatterns = [
    path('', views.truyen_list, name='truyen-list'),
    path('truyen/<slug:slug>/', views.truyen_detail, name='truyen-detail'),
]
