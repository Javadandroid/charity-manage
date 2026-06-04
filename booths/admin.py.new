from django.contrib import admin
from .models import Booth

@admin.register(Booth)
class BoothAdmin(admin.ModelAdmin):
    list_display = ('name', 'event', 'manager', 'is_active', 'product_count')
    list_filter = ('event', 'is_active')
    search_fields = ('name', 'description', 'manager__username')
    autocomplete_fields = ('event', 'manager', 'staff')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': ('name', 'description', 'event', 'image')
        }),
        ('مدیریت', {
            'fields': ('manager', 'staff')
        }),
        ('وضعیت', {
            'fields': ('is_active',)
        }),
        ('متادیتا', {
            'classes': ('collapse',),
            'fields': ('created_at', 'updated_at'),
        }),
    )
