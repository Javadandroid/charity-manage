from django.urls import path
from . import views

urlpatterns = [
    path('', views.settings_dashboard, name='settings_dashboard'),
    path('fonts/', views.font_list, name='font_list'),
    path('fonts/add/', views.font_create, name='font_create'),
    path('fonts/<int:pk>/update/', views.font_update, name='font_update'),
    path('fonts/<int:pk>/delete/', views.font_delete, name='font_delete'),
    path('system/', views.system_settings, name='system_settings'),
    path('css/fonts/', views.generate_font_css, name='custom_font_css'),
]
