from django.urls import path
from . import views

urlpatterns = [
    path('kiosk/', views.kiosk_index, name='kiosk_index'),
    path('kiosk/checkout/', views.kiosk_checkout, name='kiosk_checkout'),
    path('kiosk/pos', views.kiosk_pos_manage, name='kiosk_pos_manage'),
]
