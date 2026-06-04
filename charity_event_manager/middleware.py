from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages
from django.utils.deprecation import MiddlewareMixin

class AccessControlMiddleware(MiddlewareMixin):
    """
    میان‌افزار کنترل دسترسی برای محدود کردن دسترسی به بخش‌های مختلف سیستم
    """
    def process_request(self, request):
        # مسیرهایی که همیشه قابل دسترسی هستند
        public_urls = [
            reverse('login'), 
            reverse('logout'),
            reverse('password_reset'),
            reverse('password_reset_done'),
            # '/password-reset-confirm/', # این URL پارامتر دارد و نمی‌توان با reverse آن را دریافت کرد
            # '/password-reset-complete/', # این URL پارامتر دارد و نمی‌توان با reverse آن را دریافت کرد
            reverse('home'),
            reverse('event_list'),
            '/admin/', # شامل همه URLs ادمین
            '/static/', # فایل‌های استاتیک
            '/media/', # فایل‌های رسانه
        ]
        
        # بررسی دسترسی به admin
        if request.path.startswith('/admin/') and not request.user.is_staff:
            messages.error(request, 'شما دسترسی به پنل مدیریت را ندارید.')
            return redirect('login')
        
        # بررسی دسترسی به صفحات محافظت شده
        is_public_url = any(request.path.startswith(url) for url in public_urls)
        if not is_public_url and not request.user.is_authenticated:
            messages.warning(request, 'برای دسترسی به این صفحه باید وارد سیستم شوید.')
            return redirect('login')
            
        return None
