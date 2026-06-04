from django.db import models
from django.utils.translation import gettext_lazy as _

class Event(models.Model):
    """مدل برای نگهداری اطلاعات رویدادهای خیریه"""
    name = models.CharField(_('نام رویداد'), max_length=255)
    description = models.TextField(_('توضیحات'), blank=True, null=True)
    start_date = models.DateField(_('تاریخ شروع'))
    end_date = models.DateField(_('تاریخ پایان'))
    location = models.CharField(_('مکان'), max_length=255)
    is_active = models.BooleanField(_('فعال است؟'), default=True)
    image = models.ImageField(_('تصویر'), upload_to='events/', blank=True, null=True)
    created_at = models.DateTimeField(_('تاریخ ایجاد'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاریخ بروزرسانی'), auto_now=True)

    class Meta:
        verbose_name = _('رویداد')
        verbose_name_plural = _('رویدادها')
        ordering = ['-start_date']

    def __str__(self):
        return self.name
