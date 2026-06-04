from django.contrib import admin
from .models import Invoice, InvoiceItem

class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 0

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'booth', 'customer_name', 'total_amount', 'is_paid', 'payment_method', 'created_at')
    list_filter = ('is_paid', 'payment_method', 'created_at')
    search_fields = ('invoice_number', 'customer_name', 'customer_phone')
    inlines = [InvoiceItemInline]
