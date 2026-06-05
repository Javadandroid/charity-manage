from django import template
import jdatetime
from datetime import datetime
from django.utils import timezone

register = template.Library()

@register.filter(name='persian_numbers')
def persian_numbers(value):
    """تبدیل اعداد انگلیسی به فارسی"""
    if value is None:
        return ''
    
    value = str(value)
    # جدول تبدیل اعداد انگلیسی به فارسی
    english_to_persian = {
        '0': '۰', '1': '۱', '2': '۲', '3': '۳', '4': '۴',
        '5': '۵', '6': '۶', '7': '۷', '8': '۸', '9': '۹',
    }
    
    # جایگزینی اعداد در متن
    for eng, per in english_to_persian.items():
        value = value.replace(eng, per)
    
    return value

@register.filter(name='format_price')
def format_price(price, unit='تومان'):
    """فرمت‌دهی قیمت با جداکننده هزارگان و تبدیل به اعداد فارسی"""
    if price is None:
        return ''
    
    # جدا کردن هر سه رقم با کاما
    price = str(int(float(price)))
    price = "{:,}".format(int(price))
    
    # تبدیل به اعداد فارسی
    price = persian_numbers(price)
    
    if unit:
        return f"{price} {unit}"
    return price

@register.filter(name='jalali_date')
def jalali_date(date_obj, format_string="%Y/%m/%d"):
    """تبدیل تاریخ میلادی به هجری شمسی"""
    if not date_obj:
        return ""
    
    # اگر تاریخ به صورت رشته است، سعی کنیم آن را به شی تاریخ تبدیل کنیم
    if isinstance(date_obj, str):
        try:
            date_obj = datetime.strptime(date_obj, "%Y-%m-%d")
        except ValueError:
            return date_obj

    # تبدیل تاریخ به هجری شمسی
    try:
        # اگر datetime آگاه به منطقه زمانی است، به زمان محلی تبدیلش کنیم تا اختلاف روز رخ ندهد
        if hasattr(date_obj, 'tzinfo') and timezone.is_aware(date_obj):
            date_obj = timezone.localtime(date_obj)
        jdate = jdatetime.datetime.fromgregorian(datetime=date_obj)
        result = jdate.strftime(format_string)
        
        # تبدیل اعداد به فارسی
        return persian_numbers(result)
    except (ValueError, AttributeError):
        return ""

@register.filter(name='jalali_datetime')
def jalali_datetime(datetime_obj, format_string="%Y/%m/%d %H:%M"):
    """تبدیل تاریخ و زمان میلادی به هجری شمسی"""
    if not datetime_obj:
        return ""
    
    # تبدیل تاریخ و زمان به هجری شمسی
    try:
        # اگر datetime آگاه باشد، به زمان محلی تبدیل شود
        if hasattr(datetime_obj, 'tzinfo') and timezone.is_aware(datetime_obj):
            datetime_obj = timezone.localtime(datetime_obj)
        jdt = jdatetime.datetime.fromgregorian(datetime=datetime_obj)
        result = jdt.strftime(format_string)
        
        # تبدیل اعداد به فارسی
        return persian_numbers(result)
    except (ValueError, AttributeError):
        return ""
