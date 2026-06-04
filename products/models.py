from django.db import models
from django.utils.translation import gettext_lazy as _
from booths.models import Booth
from django.core.files.uploadedfile import InMemoryUploadedFile
from io import BytesIO
from PIL import Image, ExifTags
import sys
import os

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
    
    def formatted_price(self):
        """نمایش قیمت با فرمت مناسب"""
        return f"{self.price:,} تومان"
    
    def get_image_url(self):
        """برگرداندن آدرس تصویر محصول یا تصویر پیش‌فرض در صورت عدم وجود تصویر"""
        if self.image and hasattr(self.image, 'url'):
            return self.image.url
        return '/static/images/placeholders/product-placeholder.svg'
    
    def process_image(self, image_field):
        """
        پردازش تصویر آپلود شده برای استانداردسازی اندازه و کاهش حجم
        
        1. تصویر به حداکثر اندازه استاندارد 800x800 تغییر می‌کند
        2. حفظ نسبت ابعاد تصویر اصلی
        3. فشرده‌سازی فایل برای کاهش حجم
        4. تصحیح جهت تصویر بر اساس داده‌های EXIF
        """
        if not image_field:
            return image_field
            
        # استخراج پسوند فایل
        file_extension = os.path.splitext(image_field.name)[1]
        if file_extension.lower() not in ['.jpg', '.jpeg', '.png', '.webp']:
            return image_field  # اگر فرمت تصویر نیست، آن را پردازش نکن
        
        # باز کردن تصویر با PIL
        img = Image.open(image_field)
        
        # تصحیح چرخش تصویر بر اساس داده‌های EXIF
        try:
            for orientation in ExifTags.TAGS.keys():
                if ExifTags.TAGS[orientation] == 'Orientation':
                    if hasattr(img, '_getexif') and img._getexif():
                        exif = dict(img._getexif().items())
                        if orientation in exif:
                            if exif[orientation] == 3:
                                img = img.rotate(180, expand=True)
                            elif exif[orientation] == 6:
                                img = img.rotate(270, expand=True)
                            elif exif[orientation] == 8:
                                img = img.rotate(90, expand=True)
                    break
        except (AttributeError, KeyError, IndexError, TypeError):
            # در صورت بروز خطا در تصحیح چرخش، تصویر را بدون تغییر استفاده کن
            pass
        
        # تبدیل به RGB در صورت نیاز (برای فایل‌های RGBA مانند PNG)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # محاسبه ابعاد جدید با حفظ نسبت ابعاد
        width, height = img.size
        max_size = 800
        if width > max_size or height > max_size:
            if width > height:
                new_width = max_size
                new_height = int(height * (max_size / width))
            else:
                new_height = max_size
                new_width = int(width * (max_size / height))
            img = img.resize((new_width, new_height), Image.LANCZOS)
        
        # ذخیره با کیفیت کاهش یافته
        output = BytesIO()
        img.save(output, format='JPEG', quality=85, optimize=True)
        output.seek(0)
        
        # ایجاد آبجکت فایل جدید
        return InMemoryUploadedFile(
            output,
            'ImageField',
            f"{os.path.splitext(image_field.name)[0]}.jpg",
            'image/jpeg',
            sys.getsizeof(output),
            None
        )
    
    def save(self, *args, **kwargs):
        """
        ذخیره محصول با پردازش تصویر در صورت نیاز
        """
        # بررسی و پردازش تصویر در صورت آپلود جدید
        if self.image and hasattr(self.image, 'file') and not self.pk:
            # اگر محصول جدید است و تصویری آپلود شده
            self.image = self.process_image(self.image)
        
        # بررسی و پردازش تصویر هنگام بروزرسانی
        if self.pk:
            try:
                old_instance = Product.objects.get(pk=self.pk)
                # اگر تصویر تغییر کرده است
                if old_instance.image != self.image and self.image:
                    self.image = self.process_image(self.image)
            except Product.DoesNotExist:
                pass
                
        super().save(*args, **kwargs)
