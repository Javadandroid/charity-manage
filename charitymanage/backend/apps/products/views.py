from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Product, UnitOfMeasure
from apps.booths.models import Booth
from .serializers import ProductSerializer, UnitOfMeasureSerializer
import openpyxl
from django.db import transaction

class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        queryset = Product.objects.all()

        if not user.is_superuser:
            queryset = queryset.filter(booth__manager=user)

        event_id = self.request.query_params.get('event')
        booth_id = self.request.query_params.get('booth')

        if event_id:
            queryset = queryset.filter(booth__event_id=event_id)
        if booth_id:
            queryset = queryset.filter(booth_id=booth_id)

        return queryset

    @action(detail=False, methods=['post'], url_path='bulk-upload')
    @transaction.atomic
    def bulk_upload(self, request):
        excel_file = request.FILES.get('file')
        booth_id = request.data.get('booth_id')

        if not excel_file or not booth_id:
            return Response({"error": "فایل اکسل و شناسه غرفه الزامی است."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            booth = Booth.objects.get(pk=booth_id)

            # Additional layer of security inside the custom endpoint
            if not request.user.is_superuser and booth.manager != request.user:
                return Response({"error": "شما اجازه آپلود فایل برای این غرفه را ندارید."}, status=status.HTTP_403_FORBIDDEN)

            wb = openpyxl.load_workbook(excel_file)
            sheet = wb.active

            created_count = 0
            for row in sheet.iter_rows(min_row=2, values_only=True):
                if not row[0] or not row[1]:
                    continue

                code = str(row[0])
                name = str(row[1])
                price = row[2] or 0
                unit_id = row[3]
                description = row[4] if len(row) > 4 else ''

                unit = None
                if unit_id:
                    try:
                        unit = UnitOfMeasure.objects.get(pk=unit_id)
                    except UnitOfMeasure.DoesNotExist:
                        pass

                Product.objects.update_or_create(
                    code=code,
                    booth=booth,
                    defaults={
                        'name': name,
                        'price': price,
                        'unit': unit,
                        'description': description,
                        'is_available': True
                    }
                )
                created_count += 1

            return Response({"message": f"{created_count} محصول با موفقیت پردازش شد."}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": f"خطا در پردازش فایل: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

class UnitOfMeasureViewSet(viewsets.ModelViewSet):
    queryset = UnitOfMeasure.objects.all()
    serializer_class = UnitOfMeasureSerializer
    permission_classes = [IsAuthenticated]
