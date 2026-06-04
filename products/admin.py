from django.contrib import admin
from .models import Product, UnitOfMeasure

# Register your models here.

@admin.register(UnitOfMeasure)
class UnitOfMeasureAdmin(admin.ModelAdmin):
    list_display = ('name', 'symbol')
    search_fields = ('name', 'symbol')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'booth', 'price', 'unit', 'is_available')
    list_filter = ('booth', 'is_available', 'unit')
    search_fields = ('name', 'code', 'description')
    autocomplete_fields = ('booth', 'unit')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': ('code', 'name', 'description', 'booth', 'image')
        }),
        ('قیمت‌گذاری', {
            'fields': ('price', 'unit')
        }),
        ('وضعیت', {
            'fields': ('is_available',)
        }),
        ('متادیتا', {
            'classes': ('collapse',),
            'fields': ('created_at', 'updated_at'),
        }),
    )
