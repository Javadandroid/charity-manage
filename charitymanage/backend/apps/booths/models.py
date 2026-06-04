from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from apps.events.models import Event

class Booth(models.Model):
    """مدل برای نگهداری اطلاعات غرفه‌های رویداد"""
    event = models.ForeignKey(
        Event, 
        related_name='booths', 
        on_delete=models.CASCADE,
        verbose_name=_('رویداد')
    )
    name = models.CharField(_('نام غرفه'), max_length=255)
    description = models.TextField(_('توضیحات'), blank=True, null=True)
    manager = models.ForeignKey(
        User,
        related_name='managed_booths',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_('مدیر غرفه')
    )
    staff = models.ManyToManyField(
        User,
        related_name='booth_staff',
        blank=True,
        verbose_name=_('کارکنان غرفه')
    )
    is_active = models.BooleanField(_('فعال است؟'), default=True)
    image = models.ImageField(_('تصویر'), upload_to='booths/', blank=True, null=True)
    show_in_kiosk = models.BooleanField(_('نمایش داخل کیوسک'), default=False)
    created_at = models.DateTimeField(_('تاریخ ایجاد'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاریخ بروزرسانی'), auto_now=True)

    class Meta:
        verbose_name = _('غرفه')
        verbose_name_plural = _('غرفه‌ها')
        ordering = ['name']

    def __str__(self):
        return f"{self.name} - {self.event.name}"


class POSDevice(models.Model):
    """مدل برای نگهداری اطلاعات دستگاه‌های پوز متصل به غرفه‌ها"""
    POS_TYPES = (
        ('VERIFONE_VX520', _('Verifone VX520')),
        ('PAXS80', _('PAX S80')),
        ('INKING910', _('Inking 910')),
        ('AMP9200', _('AMP 9200')),
        ('OTHER', _('سایر')),
    )
    CONNECTION_TYPES = (
        ('TCP', _('TCP/IP')),
        ('SERIAL', _('پورت سریال')),
        ('USB', _('USB')),
    )
    BANK_TYPES = (
        ('SAMAN', _('سامان')),
        ('MELLAT', _('ملت')),
        ('PARSIAN', _('پارسیان')),
        ('PASARGAD', _('پاسارگاد')),
        ('MELLI', _('ملی')),
        ('OTHER', _('سایر')),
    )
    
    booth = models.ForeignKey(
        Booth, 
        related_name='pos_devices', 
        on_delete=models.CASCADE,
        verbose_name=_('غرفه')
    )
    name = models.CharField(_('نام دستگاه'), max_length=100)
    device_type = models.CharField(_('نوع دستگاه'), max_length=20, choices=POS_TYPES, default='VERIFONE_VX520')
    connection_type = models.CharField(_('نوع اتصال'), max_length=10, choices=CONNECTION_TYPES, default='TCP')
    bank = models.CharField(_('بانک'), max_length=10, choices=BANK_TYPES, default='SAMAN')
    ip_address = models.CharField(_('آدرس IP'), max_length=15, blank=True, null=True)
    port = models.PositiveIntegerField(_('پورت'), blank=True, null=True, default=8583)
    serial_port = models.CharField(_('پورت سریال'), max_length=20, blank=True, null=True, help_text=_('مثال: COM1'))
    baud_rate = models.PositiveIntegerField(_('نرخ باد'), blank=True, null=True, default=9600)
    terminal_id = models.CharField(_('شناسه ترمینال'), max_length=50, blank=True, null=True)
    merchant_id = models.CharField(_('شناسه پذیرنده'), max_length=50, blank=True, null=True)
    is_active = models.BooleanField(_('فعال است؟'), default=True)
    is_kiosk = models.BooleanField(_('برای کیوسک؟'), default=False)
    created_at = models.DateTimeField(_('تاریخ ایجاد'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاریخ بروزرسانی'), auto_now=True)
    
    class Meta:
        verbose_name = _('دستگاه پوز')
        verbose_name_plural = _('دستگاه‌های پوز')
        
    def __str__(self):
        return f"{self.name} - {self.get_device_type_display()} ({self.booth.name})"
