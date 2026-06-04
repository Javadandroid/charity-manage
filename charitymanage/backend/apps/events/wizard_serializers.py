from rest_framework import serializers
from .models import Event
from apps.booths.models import Booth, POSDevice
from apps.products.models import Product

class WizardProductSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    new_price = serializers.DecimalField(max_digits=10, decimal_places=0, required=False)

class WizardBoothSerializer(serializers.Serializer):
    booth_id = serializers.IntegerField()
    products = WizardProductSerializer(many=True, required=False, default=[])
    pos_devices = serializers.ListField(
        child=serializers.IntegerField(), required=False, default=[]
    )

class EventWizardSerializer(serializers.ModelSerializer):
    source_event_id = serializers.IntegerField(required=False, allow_null=True)
    booths_to_copy = WizardBoothSerializer(many=True, required=False, default=[])

    class Meta:
        model = Event
        fields = ['name', 'description', 'start_date', 'end_date', 'location', 'source_event_id', 'booths_to_copy']
