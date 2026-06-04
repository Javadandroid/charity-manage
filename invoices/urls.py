from django.urls import path
from . import views

urlpatterns = [
    path('', views.invoice_list, name='invoice_list'),
    path('api/changes/', views.invoice_changes, name='invoice_changes'),
    path('<int:pk>/', views.invoice_detail, name='invoice_detail'),
    path('create/', views.invoice_create, name='invoice_create'),
    path('create/<int:booth_id>/', views.invoice_create, name='invoice_create_for_booth'),
    path('<int:pk>/update/', views.invoice_update, name='invoice_update'),
    path('<int:pk>/delete/', views.invoice_delete, name='invoice_delete'),
    path('<int:pk>/mark-as-paid/', views.mark_invoice_as_paid, name='mark_invoice_as_paid'),
    path('<int:invoice_id>/item/<int:item_id>/toggle-delivered/', views.toggle_item_delivered, name='toggle_item_delivered'),
    path('<int:pk>/update-delivery/', views.invoice_update_delivery, name='invoice_update_delivery'),
    path('<int:pk>/update-payment/', views.invoice_update_payment, name='invoice_update_payment'),
    path('<int:pk>/toggle-all-delivery/', views.toggle_all_items_delivery, name='toggle_all_items_delivery'),
    path('<int:pk>/print/', views.print_invoice, name='print_invoice'),
    path('booth/<int:booth_id>/products/', views.get_booth_products, name='get_booth_products'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/api/', views.dashboard_api, name='dashboard_api'),
    # Admin-only bulk delete of all invoices
    path('delete-all/', views.invoices_delete_all, name='invoices_delete_all'),
]
