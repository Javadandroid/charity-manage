from rest_framework import serializers
from .models import Booth, POSDevice
from apps.events.serializers import EventSerializer

class BoothSerializer(serializers.ModelSerializer):
    event_details = EventSerializer(source='event', read_only=True)
    
    class Meta:
        model = Booth
        fields = '__all__'

class POSDeviceSerializer(serializers.ModelSerializer):
    booth_details = BoothSerializer(source='booth', read_only=True)
    
    class Meta:
        model = POSDevice
        fields = '__all__'
