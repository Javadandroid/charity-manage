from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAdminUser
from .models import Booth, POSDevice
from .serializers import BoothSerializer, POSDeviceSerializer
from .services.pos_service import send_to_pos
from apps.invoices.models import Invoice

class BoothViewSet(viewsets.ModelViewSet):
    serializer_class = BoothSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        queryset = Booth.objects.all()
        event_id = self.request.query_params.get('event')
        if event_id:
            queryset = queryset.filter(event_id=event_id)
        return queryset

class POSDeviceViewSet(viewsets.ModelViewSet):
    queryset = POSDevice.objects.all()
    serializer_class = POSDeviceSerializer
    permission_classes = [IsAdminUser]

    @action(detail=True, methods=['post'], url_path='send-payment', permission_classes=[IsAuthenticatedOrReadOnly])
    def send_payment(self, request, pk=None):
        pos_device = self.get_object()
        amount = request.data.get('amount')
        invoice_id = request.data.get('invoice_id')
        
        if not amount:
            return Response({"detail": "مبلغ (amount) الزامی است."}, status=status.HTTP_400_BAD_REQUEST)
            
        success, error_msg = send_to_pos(pos_device, amount)

        if success:
            if invoice_id:
                try:
                    invoice = Invoice.objects.get(pk=invoice_id)
                    invoice.is_paid = True
                    invoice.payment_method = 'card'
                    invoice.pos_provider = pos_device.bank
                    invoice.save()
                except Invoice.DoesNotExist:
                    pass
            return Response({"detail": "پرداخت با موفقیت انجام شد."}, status=status.HTTP_200_OK)
        else:
            return Response({"detail": error_msg}, status=status.HTTP_400_BAD_REQUEST)
