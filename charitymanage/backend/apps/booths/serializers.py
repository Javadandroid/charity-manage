from rest_framework import serializers
from .models import Booth, POSDevice

class POSDeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = POSDevice
        fields = '__all__'

class BoothSerializer(serializers.ModelSerializer):
    pos_devices = POSDeviceSerializer(many=True, read_only=True)
    
    class Meta:
        model = Booth
        fields = '__all__'
