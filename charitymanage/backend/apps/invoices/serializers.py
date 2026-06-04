from rest_framework import serializers
from .models import Invoice, InvoiceItem
from apps.products.serializers import ProductSerializer

class InvoiceItemSerializer(serializers.ModelSerializer):
    product_details = ProductSerializer(source='product', read_only=True)
    
    class Meta:
        model = InvoiceItem
        fields = '__all__'
        read_only_fields = ['invoice']

class InvoiceSerializer(serializers.ModelSerializer):
    items = InvoiceItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = Invoice
        fields = '__all__'
        read_only_fields = ['invoice_number', 'created_by']
