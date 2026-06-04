from django.contrib import admin
from .models import Product, UnitOfMeasure

@admin.register(UnitOfMeasure)
class UnitOfMeasureAdmin(admin.ModelAdmin):
    list_display = ('name', 'symbol')
    search_fields = ('name', 'symbol')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'booth', 'price', 'is_available')
    list_filter = ('booth__event', 'booth', 'is_available')
    search_fields = ('name', 'code')
