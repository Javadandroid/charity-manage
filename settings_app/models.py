from django.db import models
from django.utils.translation import gettext_lazy as _

# تابع برای تعیین مسیر ذخیره فایل‌های فونت
def font_file_path(instance, filename):
    return f'fonts/{filename}'

class Font(models.Model):
    """مدل برای نگهداری فونت‌های سیستم"""
    FONT_TYPES = (
        ('primary', _('فونت اصلی')),
        ('secondary', _('فونت ثانویه')),
        ('heading', _('عناوین')),
    )
    
    name = models.CharField(_('نام فونت'), max_length=100)
    description = models.TextField(_('توضیحات'), blank=True, null=True)
    font_file = models.FileField(_('فایل فونت'), upload_to=font_file_path, help_text=_('فایل فونت باید در فرمت TTF یا WOFF باشد'))
    font_type = models.CharField(_('نوع فونت'), max_length=20, choices=FONT_TYPES, default='primary')
    is_active = models.BooleanField(_('فعال است؟'), default=True)
    created_at = models.DateTimeField(_('تاریخ ایجاد'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاریخ بروزرسانی'), auto_now=True)
    
    class Meta:
        verbose_name = _('فونت')
        verbose_name_plural = _('فونت‌ها')
    
    def __str__(self):
        return self.name

class SystemSetting(models.Model):
    """مدل برای نگهداری تنظیمات سیستم"""
    site_title = models.CharField(_('عنوان سایت'), max_length=100, default='سیستم مدیریت رویدادهای خیریه')
    logo = models.ImageField(_('لوگو'), upload_to='settings/', blank=True, null=True)
    primary_color = models.CharField(_('رنگ اصلی'), max_length=20, default='#0d6efd')
    secondary_color = models.CharField(_('رنگ ثانویه'), max_length=20, default='#6c757d')
    primary_font = models.ForeignKey(Font, on_delete=models.SET_NULL, null=True, blank=True, related_name='primary_settings', verbose_name=_('فونت اصلی'))
    items_per_page = models.IntegerField(_('تعداد آیتم در هر صفحه'), default=20, 
                                      help_text=_('تعداد آیتم‌هایی که در هر صفحه از لیست‌ها نمایش داده می‌شود (بین 10 تا 100)'))
    
    class Meta:
        verbose_name = _('تنظیمات سیستم')
        verbose_name_plural = _('تنظیمات سیستم')
    
    def __str__(self):
        return self.site_title
        
    @classmethod
    def get_settings(cls):
        """گرفتن تنظیمات فعال یا ایجاد یک نمونه جدید اگر وجود نداشته باشد"""
        settings_obj, created = cls.objects.get_or_create(pk=1)
        return settings_obj
