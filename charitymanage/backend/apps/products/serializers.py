from rest_framework import serializers
from .models import UnitOfMeasure, Product
from apps.booths.serializers import BoothSerializer

class UnitOfMeasureSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnitOfMeasure
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    unit_details = UnitOfMeasureSerializer(source='unit', read_only=True)
    booth_details = BoothSerializer(source='booth', read_only=True)
    
    class Meta:
        model = Product
        fields = '__all__'
