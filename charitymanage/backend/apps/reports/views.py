from rest_framework.views import APIView
from rest_framework.response import Response
from apps.events.models import Event
from apps.invoices.models import Invoice
from django.db.models import Sum

class DashboardStatsView(APIView):
    def get(self, request):
        active_event = Event.objects.filter(is_active=True).first()
        if not active_event:
            return Response({"error": "No active event"}, status=404)

        invoices = Invoice.objects.filter(booth__event=active_event)

        total_sales = invoices.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        total_donations = invoices.aggregate(Sum('donation_amount'))['donation_amount__sum'] or 0
        invoice_count = invoices.count()

        return Response({
            "total_sales": total_sales,
            "total_donations": total_donations,
            "invoice_count": invoice_count
        })

class MarketReportView(APIView):
    def get(self, request):
        return Response({})

class ProductSalesReportView(APIView):
    def get(self, request):
        return Response({})

class CustomerPhonesReportView(APIView):
    def get(self, request):
        return Response({})
