from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from .models import Booth, POSDevice
from .serializers import BoothSerializer, POSDeviceSerializer
from .services import POSService

class BoothViewSet(viewsets.ModelViewSet):
    queryset = Booth.objects.all()
    serializer_class = BoothSerializer
    
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAdminUser()]

class POSDeviceViewSet(viewsets.ModelViewSet):
    queryset = POSDevice.objects.all()
    serializer_class = POSDeviceSerializer
    
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAdminUser()]
        
    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def send_amount(self, request, pk=None):
        pos_device = self.get_object()
        amount = request.data.get('amount')
        
        if not amount:
            return Response({'error': 'Amount is required'}, status=400)
            
        if pos_device.connection_type == 'TCP':
            success, message = POSService.send_to_pos_tcp(pos_device, amount)
        elif pos_device.connection_type == 'SERIAL':
            success, message = POSService.send_to_pos_serial(pos_device, amount)
        else:
            success, message = False, 'Unsupported connection type'
            
        if success:
            return Response({'success': True, 'message': 'Amount sent successfully'})
        return Response({'success': False, 'message': message}, status=400)
