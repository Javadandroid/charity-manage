from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .models import Product, UnitOfMeasure
from .serializers import ProductSerializer, UnitOfMeasureSerializer

class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        queryset = Product.objects.all()
        event_id = self.request.query_params.get('event')
        booth_id = self.request.query_params.get('booth')

        if event_id:
            queryset = queryset.filter(booth__event_id=event_id)
        if booth_id:
            queryset = queryset.filter(booth_id=booth_id)

        return queryset

class UnitOfMeasureViewSet(viewsets.ModelViewSet):
    queryset = UnitOfMeasure.objects.all()
    serializer_class = UnitOfMeasureSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
