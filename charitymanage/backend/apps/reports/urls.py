from django.urls import path
from .views import MarketReportView, ProductSalesReportView, CustomerPhonesReportView

urlpatterns = [
    path('market/', MarketReportView.as_view(), name='market_report'),
    path('product-sales/', ProductSalesReportView.as_view(), name='product_sales_report'),
    path('customer-phones/', CustomerPhonesReportView.as_view(), name='customer_phones_report'),
]
