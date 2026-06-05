def _send_via_bridge(pos_device, amount):
    """ارسال مبلغ از طریق سرویس Bridge محلی (HTTP)."""
    if not getattr(settings, 'POS_BRIDGE_URL', ''):
        return False, 'POS_BRIDGE_URL تنظیم نشده است.'
    url = settings.POS_BRIDGE_URL.rstrip('/') + '/pay'
    payload = {
        'amount': int(amount),
        'bank': pos_device.bank,
        'device_type': pos_device.device_type,
        'terminal_id': pos_device.terminal_id,
        'merchant_id': pos_device.merchant_id,
        'connection_type': pos_device.connection_type,
        'ip_address': pos_device.ip_address,
        'port': pos_device.port,
        'serial_port': pos_device.serial_port,
        'baud_rate': pos_device.baud_rate,
    }
    try:
        resp = requests.post(url, json=payload, timeout=15)
        data = resp.json() if resp.headers.get('content-type','').startswith('application/json') else {}
        if resp.ok and isinstance(data, dict) and data.get('ok'):
            return True, ''
        msg = data.get('message') if isinstance(data, dict) else resp.text
        return False, msg or 'Bridge error'
    except requests.RequestException as e:
        return False, f'Bridge connection error: {e}'

from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.db.models import Sum, Count
from django.http import JsonResponse
import socket
import serial
import json
import requests

from .models import Booth, POSDevice
from .forms import BoothForm, POSDeviceForm
from events.models import Event
from products.models import Product
from invoices.models import Invoice
from kiosk.payments import PosPasargadClient

# Create your views here.
PASARGAD_TEST_MODE = True

@login_required
def booth_list(request):
    """نمایش لیست غرفه‌ها"""
    # اگر کاربر ادمین باشد، تمام غرفه‌ها را نشان دهید
    if request.user.is_staff:
        booths = Booth.objects.all()
    else:
        # در غیر این صورت، فقط غرفه‌هایی که کاربر مدیر یا کارمند آن‌هاست را نشان دهید
        managed_booths = Booth.objects.filter(manager=request.user)
        staff_booths = Booth.objects.filter(staff=request.user)
        booths = (managed_booths | staff_booths).distinct()
    
    context = {
        'booths': booths,
        'title': _('غرفه‌های رویدادها')
    }
    return render(request, 'booths/booth_list.html', context)

@login_required
def booth_detail(request, pk):
    """نمایش جزئیات یک غرفه"""
    booth = get_object_or_404(Booth, pk=pk)
    
    # چک کنید که آیا کاربر اجازه دسترسی به این غرفه را دارد
    if not request.user.is_staff and request.user != booth.manager and request.user not in booth.staff.all():
        messages.error(request, _('شما اجازه دسترسی به این غرفه را ندارید.'))
        return redirect('booth_list')
    
    # گرفتن محصولات غرفه
    products = Product.objects.filter(booth=booth, is_available=True)
    
    # محاسبه آمار غرفه
    stats = {
        'product_count': products.count(),
        'total_sales': booth.total_sales(),
        'invoice_count': Invoice.objects.filter(booth=booth).count(),
    }
    
    context = {
        'booth': booth,
        'products': products,
        'stats': stats,
        'title': booth.name
    }
    return render(request, 'booths/booth_detail.html', context)

@login_required
def booth_create(request, event_id=None):
    """ایجاد غرفه جدید"""
    # اطمینان از دسترسی کاربر برای ایجاد غرفه
    if not request.user.is_staff:
        messages.error(request, _('شما اجازه ایجاد غرفه جدید را ندارید.'))
        return redirect('booth_list')
    
    # اگر شناسه رویداد ارائه شده باشد، آن را بازیابی کنید
    event = None
    if event_id:
        event = get_object_or_404(Event, pk=event_id)
    
    if request.method == 'POST':
        form = BoothForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            booth = form.save()
            messages.success(request, _('غرفه با موفقیت ایجاد شد.'))
            
            # در صورت ایجاد از طریق صفحه رویداد، به صفحه جزئیات رویداد برگردید
            if event:
                return redirect('event_detail', pk=event.pk)
            return redirect('booth_detail', pk=booth.pk)
    else:
        # اگر رویداد از قبل تعیین شده باشد، آن را در فرم قرار دهید
        initial_data = {}
        if event:
            initial_data['event'] = event
        form = BoothForm(initial=initial_data, user=request.user)
    
    context = {
        'form': form,
        'event': event,
        'title': _('ایجاد غرفه جدید')
    }
    return render(request, 'booths/booth_form.html', context)

@login_required
def booth_update(request, pk):
    """ویرایش غرفه"""
    booth = get_object_or_404(Booth, pk=pk)
    
    # اطمینان از دسترسی کاربر برای ویرایش غرفه
    if not request.user.is_staff and request.user != booth.manager:
        messages.error(request, _('شما اجازه ویرایش این غرفه را ندارید.'))
        return redirect('booth_detail', pk=booth.pk)
    
    if request.method == 'POST':
        form = BoothForm(request.POST, request.FILES, instance=booth, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, _('غرفه با موفقیت بروزرسانی شد.'))
            return redirect('booth_detail', pk=booth.pk)
    else:
        form = BoothForm(instance=booth, user=request.user)
    
    context = {
        'form': form,
        'booth': booth,
        'title': _('ویرایش غرفه')
    }
    return render(request, 'booths/booth_form.html', context)

@login_required
def booth_delete(request, pk):
    """حذف غرفه"""
    booth = get_object_or_404(Booth, pk=pk)
    
    # اطمینان از دسترسی کاربر برای حذف غرفه
    if not request.user.is_staff:
        messages.error(request, _('شما اجازه حذف این غرفه را ندارید.'))
        return redirect('booth_detail', pk=booth.pk)
    
    if request.method == 'POST':
        event = booth.event  # ذخیره رویداد قبل از حذف
        booth.delete()
        messages.success(request, _('غرفه با موفقیت حذف شد.'))
        return redirect('event_detail', pk=event.pk)
    
    context = {
        'booth': booth,
        'title': _('حذف غرفه')
    }
    return render(request, 'booths/booth_confirm_delete.html', context)

@login_required
def booth_dashboard(request, pk):
    """داشبورد آماری غرفه"""
    booth = get_object_or_404(Booth, pk=pk)
    
    # اطمینان از دسترسی کاربر به داشبورد غرفه
    if not request.user.is_staff and request.user != booth.manager and request.user not in booth.staff.all():
        messages.error(request, _('شما اجازه دسترسی به داشبورد این غرفه را ندارید.'))
        return redirect('booth_list')
    
    # محاسبه آمار فروش به تفکیک محصول
    product_sales = Product.objects.filter(booth=booth).annotate(
        sales=Sum('invoice_items__price'),
        quantity_sold=Sum('invoice_items__quantity'),
        count=Count('invoice_items')
    ).filter(count__gt=0).order_by('-sales')
    
    # محاسبه مجموع فروش، همت عالی و سایر آمارها
    total_sales = booth.total_sales()
    total_donations = booth.total_donations()
    invoice_count = Invoice.objects.filter(booth=booth).count()
    
    # محاسبه فروش کارتی و نقدی
    card_sales = Invoice.objects.filter(booth=booth, payment_method='card').aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    cash_sales = Invoice.objects.filter(booth=booth, payment_method='cash').aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    
    # فاکتورهای اخیر
    recent_invoices = Invoice.objects.filter(booth=booth).order_by('-created_at')[:5]
    
    stats = {
        'total_donations': total_donations,
        'total_sales': total_sales,
        'invoice_count': invoice_count,
        'card_sales': card_sales,
        'cash_sales': cash_sales,
    }
    
    context = {
        'booth': booth,
        'product_sales': product_sales,
        'total_sales': total_sales,
        'recent_invoices': recent_invoices,
        'stats': stats,
        'title': _('داشبورد غرفه {0}').format(booth.name)
    }
    return render(request, 'booths/booth_dashboard.html', context)

@login_required
def booth_stats_api(request, pk):
    """API برای گرفتن آمار غرفه - برای استفاده در نمودارها"""
    booth = get_object_or_404(Booth, pk=pk)
    
    # اطمینان از دسترسی کاربر به داده‌های آماری غرفه
    if not request.user.is_staff and request.user != booth.manager and request.user not in booth.staff.all():
        return JsonResponse({'error': 'دسترسی غیر مجاز'}, status=403)
    
    # پارامتر تاریخ برای فیلتر محصولات پرفروش (فرمت YYYY-MM-DD)
    from datetime import datetime
    selected_date = None
    date_str = request.GET.get('date')
    if date_str:
        try:
            selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except Exception:
            selected_date = None

    # تعداد محصولات پرفروش برای نمودار دایره‌ای
    from django.db.models.functions import Coalesce
    from django.db.models import Value
    if selected_date:
        # فیلتر اقلام فاکتور بر اساس تاریخ انتخاب‌شده
        top_products_qs = Product.objects.filter(
            booth=booth,
            invoice_items__invoice__created_at__date=selected_date
        ).annotate(
            quantity=Coalesce(Sum('invoice_items__quantity'), Value(0)),
            count=Count('invoice_items')
        ).filter(count__gt=0).order_by('-quantity')
    else:
        top_products_qs = Product.objects.filter(booth=booth).annotate(
            quantity=Coalesce(Sum('invoice_items__quantity'), Value(0)),
            count=Count('invoice_items')
        ).filter(count__gt=0).order_by('-quantity')
    top_products = list(top_products_qs.values('name', 'quantity'))
    
    # آمار فروش روزانه برای نمودار خطی
    from django.db.models.functions import TruncDate
    
    sales_trend = Invoice.objects.filter(booth=booth).annotate(
        date=TruncDate('created_at')
    ).values('date').annotate(
        amount=Sum('total_amount'),
        count=Count('id')
    ).order_by('date')
    
    # تبدیل تاریخ‌ها به فرمت رشته برای جاوااسکریپت
    formatted_sales_trend = []
    for item in sales_trend:
        formatted_sales_trend.append({
            'date': item['date'].strftime('%Y-%m-%d'),
            'amount': item['amount'],
            'count': item['count']
        })
    
    # استخراج فهرست روزهایی که برای این غرفه فاکتور ثبت شده است
    invoice_days_qs = Invoice.objects.filter(booth=booth).annotate(
        date=TruncDate('created_at')
    ).values('date').annotate(count=Count('id')).order_by('date')
    invoice_dates = [
        {
            'date': d['date'].strftime('%Y-%m-%d'),
            'count': d['count']
        } for d in invoice_days_qs
    ]
    
    return JsonResponse({
        'top_products': top_products,
        'sales_trend': formatted_sales_trend,
        'booth_name': booth.name,
        'invoice_dates': invoice_dates
    })

@login_required
def booth_products_api(request, pk):
    """API برای دریافت محصولات یک غرفه"""
    booth = get_object_or_404(Booth, pk=pk)
    
    # اطمینان از دسترسی کاربر به داده‌های محصولات غرفه
    if not request.user.is_staff and request.user != booth.manager and request.user not in booth.staff.all():
        return JsonResponse({'error': 'دسترسی غیر مجاز'}, status=403)
    
    # دریافت فقط محصولات موجود غرفه
    products = Product.objects.filter(booth=booth, is_available=True)
    
    # تبدیل به فرمت JSON
    products_data = []
    for product in products:
        products_data.append({
            'id': product.id,
            'name': product.name,
            'code': product.code,
            'price': product.price,
            'is_available': product.is_available,
            'unit': product.unit.name if product.unit else '',
            'image': product.get_image_url() if hasattr(product, 'get_image_url') else None,
            'description': product.description if hasattr(product, 'description') else '',
            'discount_percent': product.discount_percent if hasattr(product, 'discount_percent') else 0,
        })
    
    return JsonResponse(products_data, safe=False)

@login_required
def pos_device_list(request, booth_id):
    """نمایش لیست دستگاه‌های پوز یک غرفه"""
    booth = get_object_or_404(Booth, pk=booth_id)
    
    # چک کنید که آیا کاربر اجازه دسترسی به این غرفه را دارد
    if not request.user.is_staff and request.user != booth.manager and request.user not in booth.staff.all():
        messages.error(request, _('شما اجازه دسترسی به این غرفه را ندارید.'))
        return redirect('booth_list')
    
    pos_devices = POSDevice.objects.filter(booth=booth)
    # پوز های کیوسک را نمایش نمیدهد
    if getattr(settings, 'HIDE_KIOSK_POS_IN_BOOTH', True):
        pos_devices = pos_devices.exclude(is_kiosk=True)
    
    context = {
        'booth': booth,
        'pos_devices': pos_devices,
        'title': _('دستگاه‌های پوز غرفه {0}').format(booth.name)
    }
    return render(request, 'booths/pos_device_list.html', context)

@login_required
def pos_device_create(request, booth_id):
    """ایجاد دستگاه پوز جدید برای غرفه"""
    booth = get_object_or_404(Booth, pk=booth_id)
    
    # چک کنید که آیا کاربر اجازه دسترسی به این غرفه را دارد
    if not request.user.is_staff and request.user != booth.manager:
        messages.error(request, _('شما اجازه افزودن دستگاه پوز به این غرفه را ندارید.'))
        return redirect('booth_detail', pk=booth_id)
    
    if request.method == 'POST':
        form = POSDeviceForm(request.POST, booth=booth)
        if form.is_valid():
            pos_device = form.save(commit=False)
            pos_device.booth = booth
            pos_device.save()
            messages.success(request, _('دستگاه پوز با موفقیت اضافه شد.'))
            return redirect('pos_device_list', booth_id=booth_id)
    else:
        form = POSDeviceForm(booth=booth)
    
    context = {
        'form': form,
        'booth': booth,
        'title': _('افزودن دستگاه پوز جدید')
    }
    return render(request, 'booths/pos_device_form.html', context)

@login_required
def pos_device_update(request, pk):
    """ویرایش دستگاه پوز"""
    pos_device = get_object_or_404(POSDevice, pk=pk)
    booth = pos_device.booth
    
    # چک کنید که آیا کاربر اجازه دسترسی به این غرفه را دارد
    if not request.user.is_staff and request.user != booth.manager:
        messages.error(request, _('شما اجازه ویرایش دستگاه پوز این غرفه را ندارید.'))
        return redirect('booth_detail', pk=booth.pk)
    
    if request.method == 'POST':
        form = POSDeviceForm(request.POST, instance=pos_device)
        if form.is_valid():
            form.save()
            messages.success(request, _('دستگاه پوز با موفقیت بروزرسانی شد.'))
            return redirect('pos_device_list', booth_id=booth.pk)
    else:
        form = POSDeviceForm(instance=pos_device)
    
    context = {
        'form': form,
        'pos_device': pos_device,
        'booth': booth,
        'title': _('ویرایش دستگاه پوز')
    }
    return render(request, 'booths/pos_device_form.html', context)

@login_required
def pos_device_delete(request, pk):
    """حذف دستگاه پوز"""
    pos_device = get_object_or_404(POSDevice, pk=pk)
    booth = pos_device.booth
    
    # چک کنید که آیا کاربر اجازه دسترسی به این غرفه را دارد
    if not request.user.is_staff and request.user != booth.manager:
        messages.error(request, _('شما اجازه حذف دستگاه پوز این غرفه را ندارید.'))
        return redirect('booth_detail', pk=booth.pk)
    
    if request.method == 'POST':
        pos_device.delete()
        messages.success(request, _('دستگاه پوز با موفقیت حذف شد.'))
        return redirect('pos_device_list', booth_id=booth.pk)
    
    context = {
        'pos_device': pos_device,
        'booth': booth,
        'title': _('حذف دستگاه پوز')
    }
    return render(request, 'booths/pos_device_confirm_delete.html', context)

@login_required
def send_to_pos(request, invoice_id=None, pos_device_id=None):
    """ارسال مبلغ به دستگاه پوز"""
    if request.method == 'POST':
        # اگر از طریق فرم ارسال شده باشد
        invoice_id = request.POST.get('invoice_id')
        pos_device_id = request.POST.get('pos_device_id')
        amount = request.POST.get('amount')
    
    invoice = None
    if invoice_id:
        invoice = get_object_or_404(Invoice, pk=invoice_id)
        pos_device_id = pos_device_id or request.GET.get('pos_device_id')
        amount = invoice.total_amount
    else:
        # اگر فاکتور نداریم، مبلغ باید مستقیماً ارسال شده باشد
        amount = request.GET.get('amount')
        pos_device_id = pos_device_id or request.GET.get('pos_device_id')
    
    if not pos_device_id:
        if invoice and invoice.booth:
            # اگر فقط یک دستگاه پوز فعال برای غرفه وجود دارد، از آن استفاده می‌کنیم
            pos_devices = POSDevice.objects.filter(booth=invoice.booth, is_active=True)
            if getattr(settings, 'HIDE_KIOSK_POS_IN_BOOTH', True):
                pos_devices = pos_devices.exclude(is_kiosk=True)
            if pos_devices.count() == 1:
                pos_device = pos_devices.first()
            elif pos_devices.count() > 1:
                # اگر چند دستگاه پوز وجود دارد، فرم انتخاب دستگاه را نشان می‌دهیم
                context = {
                    'invoice': invoice,
                    'pos_devices': pos_devices,
                    'title': _('انتخاب دستگاه پوز')
                }
                return render(request, 'booths/select_pos_device.html', context)
            else:
                messages.error(request, _('هیچ دستگاه پوز فعالی برای این غرفه تعریف نشده است.'))
                if invoice:
                    return redirect('invoice_detail', pk=invoice.pk)
                return redirect('booth_list')
        else:
            messages.error(request, _('دستگاه پوز مشخص نشده است.'))
            if invoice:
                return redirect('invoice_detail', pk=invoice.pk)
            return redirect('booth_list')
    else:
        pos_device = get_object_or_404(POSDevice, pk=pos_device_id)
    
    # مبلغ‌ها در سیستم به تومان هستند؛ برای پاسارگاد از sale_toman استفاده می‌کنیم (خودش ×10 می‌کند)
    amount_toman = int(amount) if amount else 0
    
    # ارسال مبلغ به دستگاه پوز بر اساس نوع اتصال
    result = False
    error_message = ''
    
    pos_res = None
    try:
        # مسیر مستقیم پاسارگاد با کلاینت پایتونی
        if pos_device.bank == 'PASARGAD' and pos_device.connection_type == 'TCP':
            ip = pos_device.ip_address
            port = pos_device.port
            if not ip or not port:
                error_message = _('IP/Port دستگاه پوز تنظیم نشده است.')
            else:
                client = PosPasargadClient(ip=str(ip), port=int(port), timeout_ms=getattr(settings, 'POS_TIMEOUT_MS', 30000), debug=getattr(settings, 'POS_DEBUG', False))
                pos_res = client.sale_toman(amount_toman)
                result = bool(pos_res.get('ok'))
                if not result:
                    error_message = pos_res.get('message_fa') or pos_res.get('error_name') or _('خطای نامشخص')
        else:
            if pos_device.connection_type == 'TCP':
                result, error_message = send_to_pos_tcp(pos_device, amount_toman)
            elif pos_device.connection_type == 'SERIAL':
                result, error_message = send_to_pos_serial(pos_device, amount_toman)
            else:
                error_message = _('نوع اتصال پشتیبانی نمی‌شود.')
    except Exception as e:
        error_message = str(e)
    
    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'
    if result:
        # ابتدا فاکتور را بروزرسانی کنیم سپس پاسخ بدهیم
        if invoice:
            try:
                invoice.is_paid = True
                invoice.payment_method = 'card'
                if pos_res:
                    invoice.pos_provider = 'PASARGAD'
                    invoice.pos_rrn = pos_res.get('rrn') or ''
                    invoice.pos_trace = pos_res.get('trace') or ''
                    invoice.pos_txn_status = pos_res.get('txn_status') or ''
                    invoice.pos_terminal = pos_res.get('terminal') or ''
                    invoice.pos_merchant = pos_res.get('merchant') or ''
                    # ذخیره ماسک کارت در صورت ارسال توسط پاسخ پوز
                    invoice.pos_card_mask = pos_res.get('card_mask') or ''
                    raw_date = pos_res.get('date') or ''
                    fmt_date = ''
                    try:
                        d = str(raw_date)
                        if len(d) >= 8:
                            # اگر تاریخ با 14 شروع می‌شود: YYYYMMDD...
                            if d.startswith('14'):
                                y = d[0:4]; m = d[4:6]; day = d[6:8]
                                fmt_date = f"{y}/{m}/{day}"
                            # اگر فرمت YYMMDD... مانند 040803 است
                            elif d[0:2].isdigit() and d[2:4].isdigit() and d[4:6].isdigit():
                                y = '14' + d[0:2]; m = d[2:4]; day = d[4:6]
                                fmt_date = f"{y}/{m}/{day}"
                    except Exception:
                        fmt_date = ''
                    invoice.pos_date = fmt_date or raw_date
                    # لاگ دیباگ اختیاری
                    # if getattr(settings, 'POS_DEBUG', False):
                    #     try:
                    #         print(json.dumps({'pos_res': pos_res}, ensure_ascii=False))
                    #     except Exception:
                    #         pass
                    invoice.save(update_fields=['is_paid','payment_method','pos_provider','pos_rrn','pos_trace','pos_txn_status','pos_terminal','pos_merchant','pos_card_mask','pos_date'])
                else:
                    invoice.save(update_fields=['is_paid','payment_method'])
            except Exception:
                pass
        if is_ajax:
            return JsonResponse({'ok': True, 'message': str(_('پرداخت با موفقیت انجام شد.')), 'invoice_id': invoice.pk if invoice else None})
        messages.success(request, _('مبلغ با موفقیت به دستگاه پوز ارسال شد.'))
        if invoice:
            return redirect('invoice_detail', pk=invoice.pk)
        return redirect('booth_detail', pk=pos_device.booth.pk)
    else:
        if is_ajax:
            return JsonResponse({'ok': False, 'message': _('خطا در پرداخت: {0}').format(error_message)}, status=502)
        messages.error(request, _('خطا در ارسال مبلغ به دستگاه پوز: {0}').format(error_message))
        if invoice:
            return redirect('invoice_detail', pk=invoice.pk)
        return redirect('booth_detail', pk=pos_device.booth.pk)

def send_to_pos_tcp(pos_device, amount):
    """ارسال مبلغ به دستگاه پوز از طریق TCP/IP"""
    # اگر Bridge تنظیم شده و حالت تست خاموش است، از Bridge استفاده کن
    if pos_device.bank == 'PASARGAD' and getattr(settings, 'POS_BRIDGE_URL', '') and not getattr(settings, 'POS_TEST_MODE', True):
        return _send_via_bridge(pos_device, amount)
    if pos_device.bank == 'PASARGAD' and PASARGAD_TEST_MODE:
        return True, ''
    # برای Verifone VX520 بانک سامان
    if pos_device.device_type == 'VERIFONE_VX520' and pos_device.bank == 'SAMAN':
        try:
            # ساخت داده‌های ارسالی
            data = {
                'amount': amount,
                'terminal_id': pos_device.terminal_id,
                'merchant_id': pos_device.merchant_id
            }
            
            # تبدیل به رشته JSON
            json_data = json.dumps(data)
            
            # ایجاد اتصال سوکت
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)  # تایم‌اوت 10 ثانیه‌ای
            sock.connect((pos_device.ip_address, pos_device.port))
            
            # ارسال داده
            sock.sendall(json_data.encode())
            
            # دریافت پاسخ
            response = sock.recv(1024).decode()
            
            # بستن اتصال
            sock.close()
            
            # پردازش پاسخ
            if 'success' in response.lower():
                return True, ''
            else:
                return False, response
            
        except socket.error as e:
            return False, f"خطای اتصال: {str(e)}"
        except Exception as e:
            return False, f"خطای ارتباط با دستگاه پوز: {str(e)}"
    
    # برای سایر دستگاه‌ها
    return False, "این مدل دستگاه پوز یا بانک در حال حاضر پشتیبانی نمی‌شود."

def send_to_pos_serial(pos_device, amount):
    """ارسال مبلغ به دستگاه پوز از طریق پورت سریال"""
    # اگر Bridge تنظیم شده و حالت تست خاموش است، از Bridge استفاده کن
    if pos_device.bank == 'PASARGAD' and getattr(settings, 'POS_BRIDGE_URL', '') and not getattr(settings, 'POS_TEST_MODE', True):
        return _send_via_bridge(pos_device, amount)
    if pos_device.bank == 'PASARGAD' and PASARGAD_TEST_MODE:
        return True, ''
    # برای Verifone VX520 بانک سامان
    if pos_device.device_type == 'VERIFONE_VX520' and pos_device.bank == 'SAMAN':
        try:
            # ساخت داده‌های ارسالی
            command = f"AMOUNT:{amount};TERMINAL:{pos_device.terminal_id};MERCHANT:{pos_device.merchant_id}\r\n"
            
            # ایجاد اتصال سریال
            ser = serial.Serial(
                port=pos_device.serial_port,
                baudrate=pos_device.baud_rate,
                timeout=10
            )
            
            # ارسال دستور
            ser.write(command.encode())
            
            # خواندن پاسخ
            response = ser.readline().decode().strip()
            
            # بستن اتصال
            ser.close()
            
            # پردازش پاسخ
            if response.startswith('OK'):
                return True, ''
            else:
                return False, response
            
        except serial.SerialException as e:
            return False, f"خطای پورت سریال: {str(e)}"
        except Exception as e:
            return False, f"خطای ارتباط با دستگاه پوز: {str(e)}"
    
    # برای سایر دستگاه‌ها
    return False, "این مدل دستگاه پوز یا بانک در حال حاضر پشتیبانی نمی‌شود."
