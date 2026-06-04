from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.booths.models import Booth

class UnitOfMeasure(models.Model):
    """مدل برای واحدهای اندازه‌گیری محصولات"""
    name = models.CharField(_('نام واحد'), max_length=50)
    symbol = models.CharField(_('نماد'), max_length=10)
    
    class Meta:
        verbose_name = _('واحد اندازه‌گیری')
        verbose_name_plural = _('واحدهای اندازه‌گیری')
        
    def __str__(self):
        return self.name

class Product(models.Model):
    """مدل برای نگهداری اطلاعات محصولات غرفه‌ها"""
    code = models.CharField(_('کد محصول'), max_length=50, unique=True)
    name = models.CharField(_('نام محصول'), max_length=255)
    booth = models.ForeignKey(
        Booth,
        related_name='products',
        on_delete=models.CASCADE,
        verbose_name=_('غرفه')
    )
    description = models.TextField(_('توضیحات'), blank=True, null=True)
    price = models.DecimalField(_('قیمت'), max_digits=10, decimal_places=0)
    unit = models.ForeignKey(
        UnitOfMeasure,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_('واحد')
    )
    image = models.ImageField(_('تصویر محصول'), upload_to='products/', blank=True, null=True)
    is_available = models.BooleanField(_('موجود است؟'), default=True)
    created_at = models.DateTimeField(_('تاریخ ایجاد'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاریخ بروزرسانی'), auto_now=True)

    class Meta:
        verbose_name = _('محصول')
        verbose_name_plural = _('محصولات')
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.code})"
