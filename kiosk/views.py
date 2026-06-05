from django.shortcuts import render
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils.translation import gettext_lazy as _
from django.db import transaction
from django.contrib.admin.views.decorators import staff_member_required
import json

from products.models import Product
from booths.models import POSDevice, Booth
from events.models import Event
from invoices.models import Invoice, InvoiceItem

from booths.views import send_to_pos_tcp, send_to_pos_serial
from django.conf import settings
from kiosk.payments import PosPasargadClient

@require_http_methods(["GET"])
def kiosk_index(request):
    products = Product.objects.filter(is_available=True, booth__show_in_kiosk=True).select_related('booth', 'unit').order_by('booth__name', 'name')
    booths = Booth.objects.filter(is_active=True, show_in_kiosk=True, products__is_available=True).distinct().select_related('event').order_by('name')
    event_image_url = None
    event_name = ''
    if booths:
        first_event = booths.first().event
        if first_event:
            event_image_url = first_event.get_image_url()
            event_name = first_event.name
    return render(request, 'kiosk/index.html', {
        'products': products,
        'booths': booths,
        'event_image_url': event_image_url,
        'event_name': event_name,
        'title': _('کیوسک سفارش'),
        'KIOSK_INACTIVITY_SECONDS': getattr(settings, 'KIOSK_INACTIVITY_SECONDS', 60),
    })

@csrf_exempt
@csrf_exempt
@require_http_methods(["POST"])
def kiosk_checkout(request):
    try:
        cart_raw = request.POST.get('cart', '')
        phone = request.POST.get('customer_phone', '').strip()
        if not cart_raw:
            return JsonResponse({'ok': False, 'message': _('سبد خرید خالی است.')}, status=400)
        if not (len(phone) == 11 and phone.isdigit() and phone.startswith('0')):
            return JsonResponse({'ok': False, 'message': _('شماره موبایل نامعتبر است.')}, status=400)
        cart = json.loads(cart_raw)
        if not isinstance(cart, list) or not cart:
            return JsonResponse({'ok': False, 'message': _('سبد خرید نامعتبر است.')}, status=400)
        product_ids = [int(item.get('product_id')) for item in cart if int(item.get('quantity', 0)) > 0]
        quantities = {int(item['product_id']): int(item.get('quantity', 0)) for item in cart}
        products = list(Product.objects.filter(id__in=product_ids, is_available=True).select_related('booth'))
        if not products:
            return JsonResponse({'ok': False, 'message': _('هیچ محصولی یافت نشد.')}, status=400)
        booth = products[0].booth
        if any(p.booth_id != booth.id for p in products):
            return JsonResponse({'ok': False, 'message': _('امکان انتخاب از چند غرفه وجود ندارد.')}, status=400)
        pos_device = POSDevice.objects.filter(is_active=True, is_kiosk=True).first()
        if not pos_device:
            return JsonResponse({'ok': False, 'message': _('هیچ دستگاه پوز کیوسکی تنظیم نشده است.')}, status=400)
        total_amount = 0
        line_items = []
        for p in products:
            qty = max(1, quantities.get(p.id, 1))
            line_total = int(p.price) * qty
            total_amount += line_total
            line_items.append((p, qty, int(p.price)))
        result = False
        error_message = ''
        # قیمت‌ها در برنامه به تومان هستند؛ برای پاسارگاد باید ریال ارسال شود.
        # تابع sale_toman خودش عدد را ×10 می‌کند، پس اینجا تقسیم/ضرب نکنیم.
        amount_toman = int(total_amount)
        try:
            # مسیر پاسارگاد با کلاینت پایتونی جدید
            if pos_device.bank == 'PASARGAD':
                if getattr(settings, 'POS_TEST_MODE', False):
                    result = True
                else:
                    ip = pos_device.ip_address
                    port = pos_device.port
                    timeout_ms = getattr(settings, 'POS_TIMEOUT_MS', 30000)
                    debug = getattr(settings, 'POS_DEBUG', False)
                    if not ip or not port:
                        raise Exception(_('IP/Port دستگاه پوز برای "{name}" تنظیم نشده است.').format(name=pos_device.name))
                    client = PosPasargadClient(ip=ip, port=int(port), timeout_ms=int(timeout_ms), debug=bool(debug))
                    pos_res = client.sale_toman(amount_toman)
                    result = bool(pos_res.get('ok'))
                    if not result:
                        error_message = pos_res.get('message_fa') or pos_res.get('error_name') or 'خطا'
            # مسیر سایر بانک‌ها طبق روال قبلی
            else:
                if pos_device.connection_type == 'TCP':
                    result, error_message = send_to_pos_tcp(pos_device, amount_toman)
                elif pos_device.connection_type == 'SERIAL':
                    result, error_message = send_to_pos_serial(pos_device, amount_toman)
                else:
                    error_message = _('نوع اتصال پشتیبانی نمی‌شود.')
        except Exception as e:
            result = False
            error_message = str(e)
        if not result:
            return JsonResponse({'ok': False, 'message': _('خطا در پرداخت: {0}').format(error_message)}, status=502)
        with transaction.atomic():
            invoice = Invoice.objects.create(
                booth=booth,
                customer_name=_('کیوسک'),
                customer_phone=phone,
                created_by=None,
                description=None,
                donation_amount=0,
                discount_amount=0,
                total_amount=total_amount,
                is_paid=True,
                payment_method='card',
            )
            # در صورت موجود بودن پاسخ پوز، متادیتا را ذخیره می‌کنیم
            try:
                if 'pos_res' in locals() and pos_res:
                    invoice.pos_provider = 'PASARGAD'
                    invoice.pos_rrn = pos_res.get('rrn') or ''
                    invoice.pos_trace = pos_res.get('trace') or ''
                    invoice.pos_txn_status = pos_res.get('txn_status') or ''
                    invoice.pos_terminal = pos_res.get('terminal') or ''
                    invoice.pos_merchant = pos_res.get('merchant') or ''
                    invoice.pos_card_mask = pos_res.get('card_mask') or ''
                    invoice.pos_date = pos_res.get('date') or ''
                    invoice.save(update_fields=['pos_provider','pos_rrn','pos_trace','pos_txn_status','pos_terminal','pos_merchant','pos_card_mask','pos_date'])
            except Exception:
                pass

            invoice_items = [
                InvoiceItem(invoice=invoice, product=p, quantity=qty, price=unit_price)
                for p, qty, unit_price in line_items
            ]
            InvoiceItem.objects.bulk_create(invoice_items)
            invoice.update_total()

        return JsonResponse({'ok': True, 'message': _('سفارش شما ثبت شد.'), 'invoice_number': invoice.invoice_number})
    except json.JSONDecodeError:
        return JsonResponse({'ok': False, 'message': _('فرمت سبد خرید نامعتبر است.')}, status=400)
    except Exception as e:
        return JsonResponse({'ok': False, 'message': str(e)}, status=500)


@staff_member_required
@require_http_methods(["GET", "POST"])
def kiosk_pos_manage(request):
    if request.method == 'POST':
        pos_id = request.POST.get('pos_device_id')
        POSDevice.objects.update(is_kiosk=False)
        if pos_id:
            try:
                pd = POSDevice.objects.get(pk=int(pos_id))
                pd.is_kiosk = True
                pd.save()
            except POSDevice.DoesNotExist:
                pass
    devices = POSDevice.objects.filter(is_active=True).select_related('booth').order_by('bank', 'device_type', 'booth__name')
    current = POSDevice.objects.filter(is_kiosk=True).first()
    return render(request, 'kiosk/pos_manage.html', {
        'devices': devices,
        'current': current,
        'title': _('تنظیم دستگاه کیوسک'),
    })
