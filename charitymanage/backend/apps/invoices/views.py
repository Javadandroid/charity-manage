from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django.db import transaction
from .models import Invoice, InvoiceItem
from apps.products.models import Product
from .serializers import InvoiceSerializer

class InvoiceViewSet(viewsets.ModelViewSet):
    serializer_class = InvoiceSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        queryset = Invoice.objects.all()
        event_id = self.request.query_params.get('event')
        status_param = self.request.query_params.get('status')

        if event_id:
            queryset = queryset.filter(booth__event_id=event_id)

        if status_param == 'ready':
            # Example logic: we just return all invoices for the kiosk right now
            queryset = queryset.filter(is_paid=True)

        return queryset

    @action(detail=False, methods=['post'], url_path='checkout', permission_classes=[IsAuthenticatedOrReadOnly])
    @transaction.atomic
    def checkout(self, request):
        booth_id = request.data.get('booth_id')
        customer_name = request.data.get('customer_name', 'مشتری عبوری')
        items = request.data.get('items', [])

        if not booth_id or not items:
            return Response({"detail": "شناسه غرفه و لیست محصولات الزامی است."}, status=status.HTTP_400_BAD_REQUEST)

        invoice = Invoice.objects.create(
            booth_id=booth_id,
            customer_name=customer_name,
            created_by=request.user if request.user.is_authenticated else None
        )
        
        for item in items:
            product_id = item.get('product_id')
            quantity = item.get('quantity', 1)
            
            try:
                product = Product.objects.get(pk=product_id)
                InvoiceItem.objects.create(
                    invoice=invoice,
                    product=product,
                    quantity=quantity,
                    price=product.price
                )
            except Product.DoesNotExist:
                continue
                
        invoice.update_total()
        
        return Response(InvoiceSerializer(invoice).data, status=status.HTTP_201_CREATED)
