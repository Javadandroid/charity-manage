from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from django.db import transaction
from .models import Invoice, InvoiceItem
from apps.products.models import Product
from .serializers import InvoiceSerializer, InvoiceItemSerializer

class InvoiceViewSet(viewsets.ModelViewSet):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer
    
    def get_permissions(self):
        if self.action in ['create_from_cart', 'retrieve']:
            return [AllowAny()]
        return [IsAdminUser()]

    def perform_create(self, serializer):
        if self.request.user.is_authenticated:
            serializer.save(created_by=self.request.user)
        else:
            serializer.save()

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def checkout(self, request):
        """ثبت سفارش کیوسک"""
        cart = request.data.get('cart', [])
        phone = request.data.get('customer_phone', '').strip()
        customer_name = request.data.get('customer_name', 'کیوسک')
        booth_id = request.data.get('booth_id')
        
        if not cart:
            return Response({'error': 'سبد خرید خالی است.'}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            with transaction.atomic():
                total_amount = 0
                invoice = Invoice.objects.create(
                    booth_id=booth_id,
                    customer_name=customer_name,
                    customer_phone=phone,
                    created_by=request.user if request.user.is_authenticated else None,
                    is_paid=False,  # پرداخت از طریق متد جداگانه یا POS انجام می‌شود
                    total_amount=0,
                )
                
                for item in cart:
                    product_id = item.get('product_id')
                    quantity = int(item.get('quantity', 1))
                    if quantity > 0:
                        product = Product.objects.get(id=product_id)
                        price = product.price
                        InvoiceItem.objects.create(
                            invoice=invoice,
                            product=product,
                            quantity=quantity,
                            price=price
                        )
                        total_amount += (price * quantity)
                
                invoice.total_amount = total_amount
                invoice.save()
                
            serializer = self.get_serializer(invoice)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def toggle_ready(self, request, pk=None):
        """تغییر وضعیت آماده بودن فاکتور برای نوبت‌دهی"""
        invoice = self.get_object()
        invoice.is_ready = not invoice.is_ready
        invoice.save()
        
        # در صورت آماده شدن، صدا زدن نوبت کیوسک
        if invoice.is_ready:
            from apps.kiosk.services import TTSService
            tts_service = TTSService()
            # این متد صوتی را می‌سازد و آدرسش را برمی‌گرداند
            audio_url = tts_service.generate_invoice_audio(invoice.invoice_number)
            return Response({'is_ready': invoice.is_ready, 'audio_url': audio_url})
            
        return Response({'is_ready': invoice.is_ready})
