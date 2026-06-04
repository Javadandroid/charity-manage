from django.contrib import admin
from .models import Booth, POSDevice

@admin.register(Booth)
class BoothAdmin(admin.ModelAdmin):
    list_display = ('name', 'event', 'manager', 'is_active', 'show_in_kiosk')
    list_filter = ('event', 'is_active', 'show_in_kiosk')
    search_fields = ('name', 'description')

@admin.register(POSDevice)
class POSDeviceAdmin(admin.ModelAdmin):
    list_display = ('name', 'booth', 'device_type', 'bank', 'connection_type', 'is_active', 'is_kiosk')
    list_filter = ('device_type', 'bank', 'connection_type', 'is_active', 'is_kiosk')
    search_fields = ('name', 'terminal_id', 'merchant_id', 'ip_address')
