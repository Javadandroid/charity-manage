from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAdminUser
from django.db import transaction
from .models import Event
from .serializers import EventSerializer
from .wizard_serializers import EventWizardSerializer
from apps.booths.models import Booth, POSDevice
from apps.products.models import Product

class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAdminUser()]

    @action(detail=False, methods=['post'], url_path='wizard')
    @transaction.atomic
    def wizard_create(self, request):
        serializer = EventWizardSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        # Create new event
        new_event = Event.objects.create(
            name=data['name'],
            description=data.get('description', ''),
            start_date=data['start_date'],
            end_date=data['end_date'],
            location=data['location'],
            is_active=True # Will automatically deactivate others due to our save() logic
        )

        source_event_id = data.get('source_event_id')
        if source_event_id and data.get('booths_to_copy'):
            for booth_data in data['booths_to_copy']:
                try:
                    old_booth = Booth.objects.get(pk=booth_data['booth_id'], event_id=source_event_id)
                except Booth.DoesNotExist:
                    continue

                # Copy Booth
                new_booth = Booth.objects.create(
                    event=new_event,
                    name=old_booth.name,
                    description=old_booth.description,
                    manager=old_booth.manager,
                    image=old_booth.image,
                    show_in_kiosk=old_booth.show_in_kiosk
                )

                # Copy POS Devices
                for pos_id in booth_data.get('pos_devices', []):
                    try:
                        old_pos = POSDevice.objects.get(pk=pos_id, booth=old_booth)
                        POSDevice.objects.create(
                            booth=new_booth,
                            name=old_pos.name,
                            device_type=old_pos.device_type,
                            connection_type=old_pos.connection_type,
                            bank=old_pos.bank,
                            ip_address=old_pos.ip_address,
                            port=old_pos.port,
                            serial_port=old_pos.serial_port,
                            baud_rate=old_pos.baud_rate,
                            terminal_id=old_pos.terminal_id,
                            merchant_id=old_pos.merchant_id,
                            is_kiosk=old_pos.is_kiosk
                        )
                    except POSDevice.DoesNotExist:
                        pass

                # Copy Products
                for prod_data in booth_data.get('products', []):
                    try:
                        old_product = Product.objects.get(pk=prod_data['product_id'], booth=old_booth)
                        new_price = prod_data.get('new_price', old_product.price)
                        Product.objects.create(
                            code=f"{old_product.code}_copy_{new_event.pk}", # Ensure unique code
                            name=old_product.name,
                            booth=new_booth,
                            description=old_product.description,
                            price=new_price,
                            unit=old_product.unit,
                            image=old_product.image
                        )
                    except Product.DoesNotExist:
                        pass

        return Response(EventSerializer(new_event).data, status=status.HTTP_201_CREATED)
