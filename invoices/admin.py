from django.contrib import admin
from .models import Invoice, InvoiceItem

class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 1
    autocomplete_fields = ('product',)
    readonly_fields = ('total_price',)
    fields = ('product', 'quantity', 'price', 'is_delivered', 'total_price')

    def total_price(self, obj):
        if obj.pk:
            return obj.formatted_total()
        return "---"
    total_price.short_description = "قیمت کل"

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'booth', 'customer_name', 'customer_phone', 
                   'total_amount', 'donation_amount', 'is_paid', 'created_at')
    list_filter = ('booth', 'is_paid', 'created_at')
    search_fields = ('invoice_number', 'customer_name', 'customer_phone')
    readonly_fields = ('invoice_number', 'created_at', 'updated_at', 'total_amount')
    inlines = [InvoiceItemInline]
    autocomplete_fields = ('booth', 'created_by')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': ('invoice_number', 'booth', 'created_by')
        }),
        ('اطلاعات مشتری', {
            'fields': ('customer_name', 'customer_phone')
        }),
        ('اطلاعات مالی', {
            'fields': ('donation_amount', 'total_amount', 'is_paid')
        }),
        ('متادیتا', {
            'classes': ('collapse',),
            'fields': ('created_at', 'updated_at'),
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not obj.created_by:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(InvoiceItem)
class InvoiceItemAdmin(admin.ModelAdmin):
    list_display = ('invoice', 'product', 'quantity', 'price', 'total_price', 'is_delivered')
    list_filter = ('invoice__booth', 'is_delivered')
    search_fields = ('invoice__invoice_number', 'product__name')
    autocomplete_fields = ('invoice', 'product')
    
    def total_price(self, obj):
        return obj.formatted_total()
    total_price.short_description = "قیمت کل"
