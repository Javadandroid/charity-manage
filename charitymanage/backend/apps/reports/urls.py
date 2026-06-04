from django.urls import path
from .views import DashboardStatsView, MarketReportView, ProductSalesReportView, CustomerPhonesReportView

urlpatterns = [
    path('dashboard/', DashboardStatsView.as_view(), name='dashboard-stats'),
    path('market/', MarketReportView.as_view(), name='market-report'),
    path('products/', ProductSalesReportView.as_view(), name='product-report'),
    path('customers/', CustomerPhonesReportView.as_view(), name='customer-report'),
]
