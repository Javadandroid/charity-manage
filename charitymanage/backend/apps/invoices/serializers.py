from rest_framework import serializers
from .models import Invoice, InvoiceItem
from apps.products.serializers import ProductSerializer

class InvoiceItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    
    class Meta:
        model = InvoiceItem
        fields = ['id', 'product', 'product_name', 'quantity', 'price', 'is_delivered', 'total_price']

class InvoiceSerializer(serializers.ModelSerializer):
    items = InvoiceItemSerializer(many=True, read_only=True)
    booth_name = serializers.CharField(source='booth.name', read_only=True)
    
    class Meta:
        model = Invoice
        fields = '__all__'
