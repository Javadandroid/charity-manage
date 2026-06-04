from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('<int:pk>/', views.product_detail, name='product_detail'),
    path('create/', views.product_create, name='product_create'),
    path('create/<int:booth_id>/', views.product_create, name='product_create_for_booth'),
    path('<int:pk>/update/', views.product_update, name='product_update'),
    path('<int:pk>/delete/', views.product_delete, name='product_delete'),
    path('<int:pk>/toggle-availability/', views.product_toggle_availability, name='product_toggle_availability'),
    path('bulk-upload/', views.product_bulk_upload, name='product_bulk_upload'),
    
    # واحدهای اندازه‌گیری
    path('units/', views.unit_list, name='unit_list'),
    path('units/create/', views.unit_create, name='unit_create'),
    path('units/<int:pk>/update/', views.unit_update, name='unit_update'),
    path('units/<int:pk>/delete/', views.unit_delete, name='unit_delete'),
    
    # API‌های Ajax
    path('units/create-ajax/', views.create_unit_ajax, name='create_unit_ajax'),
    path('units/json/', views.get_units_json, name='get_units_json'),
    path('api/<int:pk>/', views.product_api, name='product_api'),
    path('api/create/', views.product_create_api, name='product_create_api'),
    
    # اکسل نمونه
    path('excel-template/', views.product_excel_template, name='product_excel_template'),
]
