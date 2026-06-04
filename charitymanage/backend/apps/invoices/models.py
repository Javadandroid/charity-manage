from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
from apps.booths.models import Booth
from apps.products.models import Product
import uuid
from django.db.models import Sum, F
from PIL import Image
import os
from io import BytesIO
from django.core.files.base import ContentFile

class Invoice(models.Model):
    """مدل برای نگهداری اطلاعات فاکتورهای فروش"""
    PAYMENT_METHODS = (
        ('cash', _('نقدی')),
        ('card', _('کارت')),
    )
    
    invoice_number = models.CharField(_('شماره فاکتور'), max_length=50, unique=True, editable=False)
    booth = models.ForeignKey(
        Booth,
        related_name='invoices',
        on_delete=models.CASCADE,
        verbose_name=_('غرفه')
    )
    customer_name = models.CharField(_('نام مشتری'), max_length=255)
    customer_phone = models.CharField(_('شماره موبایل'), max_length=20, blank=True, null=True)
    created_by = models.ForeignKey(
        User,
        related_name='created_invoices',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_('ایجاد کننده')
    )
    description = models.TextField(_('توضیحات'), blank=True, null=True)
    donation_amount = models.DecimalField(_('مبلغ همت عالی'), max_digits=10, decimal_places=0, default=0)
    discount_amount = models.DecimalField(_('مبلغ تخفیف'), max_digits=10, decimal_places=0, default=0)
    total_amount = models.DecimalField(_('مبلغ کل'), max_digits=10, decimal_places=0, default=0)
    is_paid = models.BooleanField(_('پرداخت شده؟'), default=False)
    payment_method = models.CharField(_('روش پرداخت'), max_length=20, choices=PAYMENT_METHODS, default='cash')
    receipt_image = models.ImageField(_('عکس فیش واریزی'), upload_to='receipts/%Y/%m/%d/', blank=True, null=True,
                                    help_text=_('فقط برای پرداخت‌های کارتی الزامی است'))
    pos_provider = models.CharField(_('پوز'), max_length=50, blank=True, null=True)
    pos_rrn = models.CharField(_('شماره پیگیری (RRN)'), max_length=32, blank=True, null=True)
    pos_trace = models.CharField(_('شماره پیگیری داخلی (Trace)'), max_length=32, blank=True, null=True)
    pos_txn_status = models.CharField(_('کد وضعیت تراکنش'), max_length=8, blank=True, null=True)
    pos_terminal = models.CharField(_('ترمینال'), max_length=32, blank=True, null=True)
    pos_merchant = models.CharField(_('پذیرنده'), max_length=64, blank=True, null=True)
    pos_card_mask = models.CharField(_('کارت (ماسک)'), max_length=64, blank=True, null=True)
    pos_date = models.CharField(_('تاریخ تراکنش (خام)'), max_length=32, blank=True, null=True)
    created_at = models.DateTimeField(_('تاریخ ایجاد'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاریخ بروزرسانی'), auto_now=True)

    class Meta:
        verbose_name = _('فاکتور')
        verbose_name_plural = _('فاکتورها')
        ordering = ['-created_at']
        permissions = [
            ("view_dashboard", "Can view dashboard"),
        ]

    def __str__(self):
        return f"{self.invoice_number} - {self.booth.name}"
    
    def save(self, *args, **kwargs):
        if not self.invoice_number:
            last_invoice = Invoice.objects.order_by('-pk').first()
            if last_invoice:
                last_number = int(last_invoice.invoice_number.replace('inv', ''))
                new_number = last_number + 1
            else:
                new_number = 1

            self.invoice_number = f"inv{new_number:06d}"

        super().save(*args, **kwargs)

        if self.receipt_image and hasattr(self.receipt_image, 'path') and os.path.exists(self.receipt_image.path):
            output_size = (800, 600)
            img = Image.open(self.receipt_image.path)

            img.thumbnail((output_size[0], output_size[1]))
            new_img = Image.new('RGB', output_size, (255, 255, 255))

            paste_x = (output_size[0] - img.size[0]) // 2
            paste_y = (output_size[1] - img.size[1]) // 2
            new_img.paste(img, (paste_x, paste_y))

            buffer = BytesIO()
            new_img.save(buffer, format='JPEG', quality=75)
            buffer.seek(0)

            file_name = os.path.basename(self.receipt_image.name)
            self.receipt_image.delete(save=False)
            self.receipt_image.save(
                file_name,
                ContentFile(buffer.read()),
                save=False
            )

            super().save(update_fields=['receipt_image'])

    def update_total(self):
        total = self.items.aggregate(total=Sum(F('price') * F('quantity')))['total'] or 0
        discount = (total * self.discount_amount / 100)
        self.total_amount = total - discount + self.donation_amount
        self.save()

    @property
    def subtotal(self):
        return sum(item.total_price for item in self.items.all())

    def formatted_total(self):
        return f"{self.total_amount:,} تومان"

    def item_count(self):
        return self.items.count()


class InvoiceItem(models.Model):
    """مدل برای آیتم‌های فاکتور"""
    invoice = models.ForeignKey(
        Invoice,
        related_name='items',
        on_delete=models.CASCADE,
        verbose_name=_('فاکتور')
    )
    product = models.ForeignKey(
        Product,
        related_name='invoice_items',
        on_delete=models.CASCADE,
        verbose_name=_('محصول')
    )
    quantity = models.PositiveIntegerField(_('تعداد'), default=1)
    price = models.DecimalField(_('قیمت واحد'), max_digits=10, decimal_places=0)
    is_delivered = models.BooleanField(_('تحویل شده؟'), default=False)
    
    class Meta:
        verbose_name = _('آیتم فاکتور')
        verbose_name_plural = _('آیتم‌های فاکتور')
    
    def __str__(self):
        return f"{self.product.name} - {self.quantity} عدد"

    @property
    def total_price(self):
        return self.quantity * self.price

    def formatted_total(self):
        return f"{self.total_price:,} تومان"

    def save(self, *args, **kwargs):
        if not self.price:
            self.price = self.product.price

        super().save(*args, **kwargs)

        self.invoice.update_total()
