from django.urls import path
from . import views

app_name = 'reports'  # اضافه کردن app_name برای namespacing

urlpatterns = [
    path('', views.report_index, name='report_index'),  # صفحه اصلی گزارشات
    path('market/', views.generate_market_report, name='market_report'),
    path('product-sales/', views.generate_product_sales_report, name='product_sales_report'), # گزارش فروش محصولات
    path('customer-phones/', views.generate_customer_phones_report, name='customer_phones_report'), # گزارش شماره تماس مشتریان
    # مسیرهای گزارش‌های دیگر را اینجا اضافه کنید
]
