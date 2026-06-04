from django.contrib import admin
from .models import Event

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date', 'location', 'is_active')
    list_filter = ('is_active', 'start_date')
    search_fields = ('name', 'description', 'location')
    date_hierarchy = 'start_date'
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': ('name', 'description', 'location', 'image')
        }),
        ('زمان‌بندی', {
            'fields': ('start_date', 'end_date')
        }),
        ('وضعیت', {
            'fields': ('is_active',)
        }),
        ('متادیتا', {
            'classes': ('collapse',),
            'fields': ('created_at', 'updated_at'),
        }),
    )
