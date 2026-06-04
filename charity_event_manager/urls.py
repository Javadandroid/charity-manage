"""
URL configuration for charity_event_manager project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from . import views
from booths.views import booth_products_api
from products.views import product_api

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # اپلیکیشن‌های اصلی
    path('events/', include('events.urls')),
    path('booths/', include('booths.urls')),
    path('products/', include('products.urls')),
    path('invoices/', include('invoices.urls')),
    path('settings/', include('settings_app.urls')),
    path('reports/', include('reports.urls')), # اضافه کردن مسیر برای اپلیکیشن گزارشات
    path('', include('kiosk.urls')),
    
    # صفحات اصلی
    path('', views.home, name='home'),
    path('dashboard/', views.user_dashboard, name='user_dashboard'),
    # Nobat (queue) display
    path('nobat', views.nobat_page, name='nobat_page'),
    path('nobat/api/current/', views.nobat_current, name='nobat_current'),
    path('nobat/api/show/', views.nobat_show, name='nobat_show'),
    # مسیر 'reports/market/' از اینجا حذف شد چون از طریق include('reports.urls') مدیریت می‌شود.
    
    # احراز هویت کاربر
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    
    # مسیرهای بازنشانی رمز عبور
    path('password-reset/', auth_views.PasswordResetView.as_view(template_name='password_reset_form.html'), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'), name='password_reset_confirm'),
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'), name='password_reset_complete'),
    
    # مسیرهای API
    path('api/booths/<int:pk>/products/', booth_products_api, name='booth_products_api'),
    path('api/products/<int:pk>/', product_api, name='product_api'),
]

# اضافه کردن مسیرهای فایل‌های استاتیک و مدیا در محیط توسعه
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
