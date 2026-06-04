from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser
from django.http import HttpResponse
from .services import ReportService

class MarketReportView(APIView):
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        excel_bytes = ReportService.generate_market_report()
        response = HttpResponse(excel_bytes, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="market_report.xlsx"'
        return response

class ProductSalesReportView(APIView):
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        excel_bytes = ReportService.generate_product_sales_report()
        response = HttpResponse(excel_bytes, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="product_sales_report.xlsx"'
        return response

class CustomerPhonesReportView(APIView):
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        excel_bytes = ReportService.generate_customer_phones_report()
        response = HttpResponse(excel_bytes, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="customer_phones_report.xlsx"'
        return response
