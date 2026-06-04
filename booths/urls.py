from django.urls import path
from . import views

urlpatterns = [
    path('', views.booth_list, name='booth_list'),
    path('<int:pk>/', views.booth_detail, name='booth_detail'),
    path('create/', views.booth_create, name='booth_create'),
    path('create/<int:event_id>/', views.booth_create, name='booth_create_for_event'),
    path('<int:pk>/update/', views.booth_update, name='booth_update'),
    path('<int:pk>/delete/', views.booth_delete, name='booth_delete'),
    path('<int:pk>/dashboard/', views.booth_dashboard, name='booth_dashboard'),
    path('<int:pk>/stats/api/', views.booth_stats_api, name='booth_stats_api'),
    path('api/<int:pk>/products/', views.booth_products_api, name='booth_products_api'),
    
    # URLs for POS devices
    path('<int:booth_id>/pos/', views.pos_device_list, name='pos_device_list'),
    path('<int:booth_id>/pos/create/', views.pos_device_create, name='pos_device_create'),
    path('pos/<int:pk>/update/', views.pos_device_update, name='pos_device_update'),
    path('pos/<int:pk>/delete/', views.pos_device_delete, name='pos_device_delete'),
    path('pos/send/', views.send_to_pos, name='send_to_pos'),
    path('pos/send/<int:invoice_id>/', views.send_to_pos, name='send_invoice_to_pos'),
    path('pos/send/<int:invoice_id>/<int:pos_device_id>/', views.send_to_pos, name='send_invoice_to_pos_device'),
]
