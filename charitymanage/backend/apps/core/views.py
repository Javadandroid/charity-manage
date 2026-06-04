from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAdminUser
from .models import Font, SystemSetting
from .serializers import FontSerializer, SystemSettingSerializer

class FontViewSet(viewsets.ModelViewSet):
    queryset = Font.objects.all()
    serializer_class = FontSerializer
    
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAdminUser()]

class SystemSettingView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request):
        setting = SystemSetting.get_settings()
        serializer = SystemSettingSerializer(setting)
        return Response(serializer.data)
        
    def put(self, request):
        if not request.user.is_staff:
            return Response({'error': 'Unauthorized'}, status=403)
        setting = SystemSetting.get_settings()
        serializer = SystemSettingSerializer(setting, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)
