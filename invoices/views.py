import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.http import JsonResponse
from django.db.models import Sum, F, Count
from django.db import transaction



from .models import Invoice, InvoiceItem
from .forms import InvoiceForm
from booths.models import Booth
from products.models import Product
from django.template.loader import render_to_string

# Create your views here.

@login_required
def invoice_list(request):
    """نمایش لیست فاکتورها با صفحه‌بندی و قابلیت جستجو"""
    # اگر کاربر ادمین باشد، تمام فاکتورها را نشان دهید
    if request.user.is_staff:
        invoices = Invoice.objects.all()
    else:
        # در غیر این صورت، فقط فاکتورهای غرفه‌هایی که کاربر مدیر یا کارمند آنهاست را نشان دهید
        managed_booths = Booth.objects.filter(manager=request.user)
        staff_booths = Booth.objects.filter(staff=request.user)
        booths = (managed_booths | staff_booths).distinct()
        invoices = Invoice.objects.filter(booth__in=booths)
    
    # دریافت همه غرفه‌ها و رویدادها برای فیلتر
    all_booths = Booth.objects.all().select_related('event').order_by('name')
    all_events = Booth.objects.values('event__id', 'event__name').distinct()
    
    # فیلتر کردن بر اساس پارامترهای URL
    filters = {}
    filter_kwargs = {}
    
    # فیلتر شماره فاکتور
    invoice_number = request.GET.get('invoice_number')
    if invoice_number:
        filters['invoice_number__icontains'] = invoice_number
    
    # فیلتر نام مشتری
    customer_name = request.GET.get('customer_name')
    if customer_name:
        filters['customer_name__icontains'] = customer_name
    
    # فیلتر رویداد
    event = request.GET.get('event')
    if event and event.isdigit():
        filters['booth__event_id'] = int(event)
    
    # فیلتر غرفه
    booth = request.GET.get('booth')
    if booth and booth.isdigit():
        filters['booth_id'] = int(booth)
    
    # فیلتر وضعیت پرداخت
    is_paid = request.GET.get('is_paid')
    if is_paid in ['0', '1']:
        filters['is_paid'] = (is_paid == '1')
    
    # فیلتر وضعیت تحویل
    is_delivered = request.GET.get('is_delivered')
    if is_delivered in ['0', '1']:
        filters['items__is_delivered'] = (is_delivered == '1')
    
    # فیلتر تاریخ - استفاده از مقادیر hidden که در فرمت میلادی هستند
    date_from_hidden = request.GET.get('date_from_hidden')
    if date_from_hidden:
        filters['created_at__gte'] = date_from_hidden
    else:
        # اگر مقدار hidden موجود نبود، از مقدار اصلی استفاده می‌کنیم (برای سازگاری با قبل)
        date_from = request.GET.get('date_from')
        if date_from and date_from.count('-') == 2:  # اگر به فرمت YYYY-MM-DD باشد
            filters['created_at__gte'] = date_from
    
    date_to_hidden = request.GET.get('date_to_hidden')
    if date_to_hidden:
        filters['created_at__lte'] = date_to_hidden
    else:
        # اگر مقدار hidden موجود نبود، از مقدار اصلی استفاده می‌کنیم (برای سازگاری با قبل)
        date_to = request.GET.get('date_to')
        if date_to and date_to.count('-') == 2:  # اگر به فرمت YYYY-MM-DD باشد
            filters['created_at__lte'] = date_to
    
    # اعمال فیلترها
    if filters:
        invoices = invoices.filter(**filters)
    
    # مرتب‌سازی
    sort_param = request.GET.get('sort', '-created_at')
    valid_sort_fields = ['created_at', '-created_at', 'total_amount', '-total_amount', 'customer_name', '-customer_name']
    if sort_param in valid_sort_fields:
        invoices = invoices.order_by(sort_param)
    else:
        invoices = invoices.order_by('-created_at')
    
    # دریافت تنظیمات تعداد آیتم در هر صفحه
    from settings_app.models import SystemSetting
    settings = SystemSetting.get_settings()
    items_per_page = settings.items_per_page
    
    # تعیین تعداد آیتم در هر صفحه از طریق پارامتر URL (اختیاری)
    per_page = request.GET.get('per_page')
    if per_page and per_page.isdigit():
        per_page_int = int(per_page)
        if 10 <= per_page_int <= 100:
            items_per_page = per_page_int
    
    # صفحه‌بندی
    from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
    paginator = Paginator(invoices, items_per_page)
    page = request.GET.get('page')
    
    try:
        invoices_page = paginator.page(page)
    except PageNotAnInteger:
        # اگر شماره صفحه یک عدد نیست، صفحه اول را نشان بده
        invoices_page = paginator.page(1)
    except EmptyPage:
        # اگر شماره صفحه خارج از محدوده است، آخرین صفحه را نشان بده
        invoices_page = paginator.page(paginator.num_pages)
    
    # ایجاد کوئری استرینگ برای پیمایش صفحات با حفظ فیلترها
    query_dict = request.GET.copy()
    if 'page' in query_dict:
        del query_dict['page']
    query_string = query_dict.urlencode()
    
    context = {
        'invoices': invoices_page,
        'title': _('فاکتورها'),
        'all_booths': all_booths,
        'all_events': all_events,
        'query_string': query_string,
        'total_invoices': paginator.count,
        'items_per_page': items_per_page,
        'per_page_options': [10, 20, 50, 100],
        'poll_seconds': getattr(settings, 'INVOICE_LIST_POLL_SECONDS', 10),
    }
    return render(request, 'invoices/invoice_list.html', context)

@login_required
def invoice_changes(request):
    """برگرداندن ردیف‌های جدید فاکتور از آخرین شناسه اعلام‌شده برای به‌روزرسانی بدون رفرش"""
    try:
        last_id = int(request.GET.get('last_id') or 0)
    except ValueError:
        last_id = 0

    # همان منطق دسترسی مانند invoice_list
    if request.user.is_staff:
        invoices = Invoice.objects.all()
    else:
        managed_booths = Booth.objects.filter(manager=request.user)
        staff_booths = Booth.objects.filter(staff=request.user)
        booths = (managed_booths | staff_booths).distinct()
        invoices = Invoice.objects.filter(booth__in=booths)

    # همان فیلترها از کوئری‌استرینگ
    filters = {}

    invoice_number = request.GET.get('invoice_number')
    if invoice_number:
        filters['invoice_number__icontains'] = invoice_number

    customer_name = request.GET.get('customer_name')
    if customer_name:
        filters['customer_name__icontains'] = customer_name

    event = request.GET.get('event')
    if event and event.isdigit():
        filters['booth__event_id'] = int(event)

    booth = request.GET.get('booth')
    if booth and booth.isdigit():
        filters['booth_id'] = int(booth)

    is_paid = request.GET.get('is_paid')
    if is_paid in ['0', '1']:
        filters['is_paid'] = (is_paid == '1')

    is_delivered = request.GET.get('is_delivered')
    if is_delivered in ['0', '1']:
        filters['items__is_delivered'] = (is_delivered == '1')

    date_from_hidden = request.GET.get('date_from_hidden')
    if date_from_hidden:
        filters['created_at__gte'] = date_from_hidden
    else:
        date_from = request.GET.get('date_from')
        if date_from and date_from.count('-') == 2:
            filters['created_at__gte'] = date_from

    date_to_hidden = request.GET.get('date_to_hidden')
    if date_to_hidden:
        filters['created_at__lte'] = date_to_hidden
    else:
        date_to = request.GET.get('date_to')
        if date_to and date_to.count('-') == 2:
            filters['created_at__lte'] = date_to

    if filters:
        invoices = invoices.filter(**filters)

    # فقط فاکتورهای جدیدتر از last_id
    if last_id > 0:
        invoices = invoices.filter(id__gt=last_id)

    invoices = invoices.order_by('-created_at')[:50]

    html = render_to_string('invoices/_invoice_rows.html', {'invoices': invoices, 'user': request.user})
    max_id =  last_id
    if invoices:
        try:
            max_id = max([inv.id for inv in invoices])
        except Exception:
            pass
    return JsonResponse({'count': len(invoices), 'max_id': max_id, 'html': html})

@login_required
def invoice_detail(request, pk):
    """نمایش جزئیات فاکتور"""
    invoice = get_object_or_404(Invoice, pk=pk)
    
    # بررسی دسترسی
    if not request.user.is_staff and request.user != invoice.booth.manager and request.user not in invoice.booth.staff.all():
        messages.error(request, _('شما اجازه دسترسی به این فاکتور را ندارید.'))
        return redirect('invoice_list')
    
    # محاسبه تعداد آیتم‌های تحویل شده
    delivered_items_count = invoice.items.filter(is_delivered=True).count()
    total_items_count = invoice.items.count()
    
    # محاسبه درصد پیشرفت تحویل
    delivery_percentage = 0
    if total_items_count > 0:
        delivery_percentage = round((delivered_items_count / total_items_count) * 100)
    
    # گرفتن آیتم‌های فاکتور
    items = invoice.items.all()
    
    context = {
        'invoice': invoice,
        'items': items,
        'delivered_items_count': delivered_items_count,
        'total_items_count': total_items_count,
        'delivery_percentage': delivery_percentage,
        'title': f'فاکتور شماره {invoice.invoice_number}'
    }
    return render(request, 'invoices/invoice_detail.html', context)

@login_required
def invoice_create(request, booth_id=None):
    """ایجاد فاکتور جدید"""
    # بررسی اینکه آیا یک غرفه خاص برای فاکتور تعیین شده است
    booth = None
    if booth_id:
        booth = get_object_or_404(Booth, pk=booth_id)
        # بررسی دسترسی کاربر به غرفه
        if not request.user.is_staff and request.user != booth.manager and request.user not in booth.staff.all():
            messages.error(request, _('شما اجازه ایجاد فاکتور برای این غرفه را ندارید.'))
            return redirect('booth_detail', pk=booth.pk)
    elif not request.user.is_staff:
        # اگر کاربر ادمین نیست و غرفه‌ای تعیین نشده، باید دسترسی به حداقل یک غرفه داشته باشد
        managed_booths = Booth.objects.filter(manager=request.user)
        staff_booths = Booth.objects.filter(staff=request.user)
        if not (managed_booths.exists() or staff_booths.exists()):
            messages.error(request, _('شما اجازه ایجاد فاکتور ندارید.'))
            return redirect('invoice_list')
    
    if request.method == 'POST':
        # بررسی اینکه آیا غرفه ارسال شده است
        post_data = request.POST.copy()  # ساخت کپی از داده‌های ارسالی برای تغییر آن
        
        # اگر نام مشتری خالی است، نام پیش‌فرض "بدون نام" استفاده شود
        if not post_data.get('customer_name', '').strip():
            post_data['customer_name'] = "بدون نام"
        
        # اگر booth_id وجود دارد، به صورت دستی اضافه شود
        if booth_id and booth and 'booth' not in post_data:
            post_data['booth'] = booth.id
            
        form = InvoiceForm(post_data, user=request.user, booth=booth)
        if form.is_valid():
            try:
                invoice = form.save(commit=False)
                invoice.created_by = request.user
                
                # اطمینان از تنظیم غرفه قبل از ذخیره
                if booth_id and booth:
                    invoice.booth = booth
                invoice.save()
                
                # پردازش آیتم‌های فاکتور از داده‌های JSON
                items_data = json.loads(post_data.get('invoice_items', '[]'))
                if not items_data:
                    # اگر هیچ آیتمی نباشد، پیام خطا نشان بده
                    invoice.delete()
                    messages.error(request, _('فاکتور باید حداقل شامل یک محصول باشد.'))
                    return render(request, 'invoices/invoice_form.html', {
                        'form': form,
                        'booth': booth,
                        'title': _('ایجاد فاکتور جدید')
                    })
                
                try:
                    for item_data in items_data:
                        product = get_object_or_404(Product, pk=item_data['product_id'])
                        
                        # اگر کاربر ادمین یا استاف نیست، از قیمت اصلی محصول استفاده کن
                        if request.user.is_staff or request.user.is_superuser:
                            price = item_data.get('price', product.price)
                        else:
                            # برای کاربران عادی، همیشه از قیمت اصلی محصول استفاده می‌شود
                            price = product.price
                        
                        InvoiceItem.objects.create(
                            invoice=invoice,
                            product=product,
                            quantity=item_data['quantity'],
                            price=price,
                            is_delivered=item_data.get('is_delivered', False)  # مقدار پیش‌فرض تحویل نشده است
                        )
                    
                    # حالا که تمام آیتم‌ها ایجاد شده‌اند، فاکتور را مجدداً ذخیره می‌کنیم تا مبلغ کل محاسبه شود
                    invoice.save()
                    
                    messages.success(request, _('فاکتور با موفقیت ایجاد شد.'))
                    return redirect('invoice_detail', pk=invoice.pk)
                except Exception as e:
                    # در صورت بروز خطا در ایجاد آیتم، فاکتور را حذف می‌کنیم
                    invoice.delete()
                    messages.error(request, _('خطا در ثبت آیتم‌های فاکتور: {0}').format(str(e)))
            except Exception as e:
                # در صورت بروز خطای کلی، فاکتور را حذف می‌کنیم
                if 'invoice' in locals() and invoice.id:
                    invoice.delete()
                messages.error(request, _('خطا در ذخیره فاکتور: {0}').format(str(e)))
        else:
            # نمایش خطاهای فرم به صورت مناسب
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, _(f'خطا در فیلد {form.fields[field].label}: {error}'))
    else:
        form = InvoiceForm(user=request.user, booth=booth)
    
    # گرفتن محصولات برای فیلد انتخاب در صفحه
    products = []
    if booth:
        products = Product.objects.filter(booth=booth, is_available=True).values(
            'id', 'name', 'code', 'price', 'unit__name'
        )
    
    context = {
        'form': form,
        'booth': booth,
        'products': list(products),
        'title': _('ایجاد فاکتور جدید'),
        'can_edit_prices': request.user.is_staff or request.user.is_superuser  # فقط ادمین‌ها می‌توانند قیمت را تغییر دهند
    }
    return render(request, 'invoices/invoice_form.html', context)

@login_required
def invoice_update(request, pk):
    """ویرایش فاکتور"""
    invoice = get_object_or_404(Invoice, pk=pk)
    
    # بررسی دسترسی کاربر به فاکتور
    if not request.user.is_staff and request.user != invoice.booth.manager and request.user not in invoice.booth.staff.all():
        messages.error(request, _('شما اجازه دسترسی به این فاکتور را ندارید.'))
        return redirect('invoice_list')
    
    # اگر درخواست POST است
    if request.method == 'POST':
        post_data = request.POST.copy()
        
        # اگر نام مشتری خالی است، نام پیش‌فرض "بدون نام" استفاده شود
        if not post_data.get('customer_name', '').strip():
            post_data['customer_name'] = "بدون نام"
        
        # بررسی آیتم‌های فاکتور
        invoice_items_json = post_data.get('invoice_items', '[]')
        
        try:
            # تبدیل JSON به آبجکت پایتون
            items_data = json.loads(invoice_items_json)
            
            # پردازش آیتم‌ها
                
            # ثبت تعداد آیتم‌های موجود در فاکتور قبل از به‌روزرسانی
            existing_items = list(InvoiceItem.objects.filter(invoice=invoice).values('id', 'product_id', 'product__name', 'quantity', 'price'))
            
            # بررسی اعتبار فرم
            form = InvoiceForm(post_data, instance=invoice, user=request.user)
            is_valid = form.is_valid()
            
            if not is_valid:
                # print(f"خطاهای فرم: {form.errors}")
                messages.error(request, 'فرم نامعتبر است. لطفاً خطاها را بررسی کنید.')
            
            if is_valid:
                # ذخیره فاکتور
                invoice = form.save(commit=False)
                invoice.updated_by = request.user
                invoice.save()
                
                # حذف تمام آیتم‌های فعلی
                old_items = list(InvoiceItem.objects.filter(invoice=invoice).values('id', 'product__name', 'quantity', 'price'))
                
                # حذف آیتم‌های قبلی
                try:
                    deleted_items = InvoiceItem.objects.filter(invoice=invoice).delete()
                except Exception:
                    # print(f"خطا در حذف آیتم‌های قبلی: {str(e)}")
                    raise
                
                # پردازش آیتم‌های جدید از JSON
                if not items_data:
                    messages.error(request, _('فاکتور باید حداقل شامل یک محصول باشد.'))
                    # print("خطا: هیچ آیتمی وجود ندارد!")
                else:
                    # ایجاد آیتم‌های جدید
                    created_items = []
                    for item_data in items_data:
                        try:
                            product_id = item_data.get('product_id')
                            quantity = item_data.get('quantity')
                            price = item_data.get('price')
                            
                            try:
                                product = get_object_or_404(Product, pk=product_id)
                            except Exception:
                                raise
                            
                            # کنترل قیمت
                            if request.user.is_staff or request.user.is_superuser:
                                price = item_data.get('price', product.price)
                            else:
                                price = product.price
                            
                            # تبدیل به عدد
                            try:
                                quantity = int(quantity)
                                price = int(price)
                            except (ValueError, TypeError):
                                price = int(product.price)
                            
                            try:
                                item = InvoiceItem.objects.create(
                                    invoice=invoice,
                                    product=product,
                                    quantity=quantity,
                                    price=price,
                                    is_delivered=item_data.get('is_delivered', False)
                                )
                                created_items.append(item)
                            except Exception:
                                raise
                        except Exception:
                            pass
                    
                    # print(f"تعداد آیتم‌های ایجاد شده: {len(created_items)}")
                    
                    # بررسی همه آیتم‌های موجود پس از ایجاد
                    try:
                        created_items_data = list(InvoiceItem.objects.filter(invoice=invoice).values('id', 'product__name', 'quantity', 'price'))
                    except Exception:
                        # print(f"خطا در دریافت آیتم‌های جدید: {str(e)}")
                        raise
                    
                    # به‌روزرسانی مبلغ کل فاکتور
                    try:
                        invoice.save()
                        messages.success(request, _('فاکتور با موفقیت به‌روزرسانی شد.'))
                        return redirect('invoice_detail', pk=invoice.pk)
                    except Exception:
                        # print(f"خطا در به‌روزرسانی فاکتور: {str(e)}")
                        raise
            else:
                # نمایش خطاهای فرم
                # print("خطاهای فرم:")
                for field, errors in form.errors.items():
                    for error in errors:
                        error_msg = _(f'خطا در فیلد {form.fields[field].label}: {error}')
                        # print(error_msg)
                        messages.error(request, error_msg)
        except Exception as e:
            # print(f"خطای کلی در به‌روزرسانی فاکتور: {str(e)}")
            messages.error(request, _('خطا در به‌روزرسانی فاکتور: {0}').format(str(e)))
    else:
        # ایجاد فرم با مقادیر فعلی فاکتور
        form = InvoiceForm(instance=invoice, user=request.user)
        
        # # چاپ اطلاعات آیتم‌های فعلی
        # print("==== آیتم‌های فعلی فاکتور ====")
        # for item in invoice.items.all():
        #     print(f"محصول: {item.product.id} - {item.product.name}, تعداد: {item.quantity}, قیمت: {item.price}")
        # print("==============================")
    
    # گرفتن محصولات غرفه برای نمایش در صفحه
    products = []
    if invoice.booth:
        # استفاده از values_list به جای values برای دریافت دیتا و حذف فیلد image برای جلوگیری از خطا
        products = Product.objects.filter(booth=invoice.booth, is_available=True).values(
            'id', 'name', 'code', 'price', 'is_available', 'unit__name', 'unit__id',
            'description'
        )
        
        # افزودن فیلد image به صورت دستی با بررسی وجود آن
        products = list(products)
        for product in products:
            try:
                # تلاش برای یافتن URL تصویر محصول
                p = Product.objects.get(id=product['id'])
                if p.image and hasattr(p.image, 'url'):
                    product['image_url'] = p.image.url
                else:
                    product['image_url'] = ''
            except Exception:
                # print(f"خطا در دریافت تصویر محصول {product['id']}: {str(e)}")
                product['image_url'] = ''
    
    context = {
        'form': form,
        'invoice': invoice,
        'products': list(products),
        'title': _('ویرایش فاکتور'),
        'booth': invoice.booth,
        'is_update': True,
        'can_edit_prices': request.user.is_staff or request.user.is_superuser
    }
    return render(request, 'invoices/invoice_form.html', context)

@login_required
def invoice_delete(request, pk):
    """حذف فاکتور"""
    invoice = get_object_or_404(Invoice, pk=pk)
    
    # بررسی دسترسی کاربر به فاکتور
    if not request.user.is_staff and request.user != invoice.booth.manager and request.user not in invoice.booth.staff.all():
        messages.error(request, _('شما اجازه دسترسی به این فاکتور را ندارید.'))
        return redirect('invoice_list')
    
    if request.method == 'POST':
        invoice.delete()
        messages.success(request, _('فاکتور با موفقیت حذف شد.'))
        return redirect('invoice_list')
    
    context = {
        'invoice': invoice,
        'title': _('حذف فاکتور')
    }
    return render(request, 'invoices/invoice_confirm_delete.html', context)

@login_required
def invoices_delete_all(request):
    """حذف کلی همه فاکتورها - فقط برای ادمین (staff) با صفحه تایید"""
    if not request.user.is_staff:
        messages.error(request, _('شما اجازه انجام این عملیات را ندارید.'))
        return redirect('invoice_list')

    if request.method == 'POST':
        try:
            with transaction.atomic():
                # حذف تمام فاکتورها (آیتم‌ها به دلیل on_delete=CASCADE حذف می‌شوند)
                deleted_count, deleted_details = Invoice.objects.all().delete()
            messages.success(request, _('تمام فاکتورها با موفقیت حذف شدند.'))
            return redirect('invoice_list')
        except Exception as e:
            messages.error(request, _('خطا در حذف کلی فاکتورها: {0}').format(str(e)))
            return redirect('invoice_list')

    # GET: نمایش صفحه تایید
    total_invoices = Invoice.objects.count()
    total_items = InvoiceItem.objects.count()
    context = {
        'title': _('حذف کلی فاکتورها'),
        'total_invoices': total_invoices,
        'total_items': total_items,
    }
    return render(request, 'invoices/invoices_confirm_delete_all.html', context)

@login_required
def mark_invoice_as_paid(request, pk):
    """علامت‌گذاری فاکتور به عنوان پرداخت شده"""
    invoice = get_object_or_404(Invoice, pk=pk)
    
    # بررسی دسترسی کاربر به فاکتور
    if not request.user.is_staff and request.user != invoice.booth.manager and request.user != invoice.created_by and request.user not in invoice.booth.staff.all():
        messages.error(request, _('شما اجازه تغییر وضعیت این فاکتور را ندارید.'))
        return redirect('invoice_detail', pk=invoice.pk)
    
    invoice.is_paid = True
    invoice.save()
    
    messages.success(request, _('فاکتور با موفقیت به عنوان پرداخت شده علامت‌گذاری شد.'))
    return redirect('invoice_detail', pk=invoice.pk)

@login_required
def toggle_item_delivered(request, invoice_id, item_id):
    """تغییر وضعیت تحویل یک آیتم فاکتور"""
    invoice = get_object_or_404(Invoice, pk=invoice_id)
    item = get_object_or_404(InvoiceItem, pk=item_id, invoice=invoice)
    
    # بررسی دسترسی کاربر به فاکتور
    if not request.user.is_staff and request.user != invoice.booth.manager and request.user != invoice.created_by and request.user not in invoice.booth.staff.all():
        messages.error(request, _('شما اجازه دسترسی به این فاکتور را ندارید.'))
        return redirect('invoice_list')
    
    # تغییر وضعیت تحویل
    item.is_delivered = not item.is_delivered
    item.save()
    
    messages.success(request, _('وضعیت تحویل آیتم با موفقیت تغییر کرد.'))
    return redirect('invoice_detail', pk=invoice_id)

@login_required
def invoice_update_delivery(request, pk):
    """به‌روزرسانی وضعیت تحویل آیتم‌های فاکتور"""
    invoice = get_object_or_404(Invoice, pk=pk)
    
    # بررسی دسترسی کاربر به فاکتور
    if not request.user.is_staff and request.user != invoice.booth.manager and request.user not in invoice.booth.staff.all():
        messages.error(request, _('شما اجازه دسترسی به این فاکتور را ندارید.'))
        return redirect('invoice_list')
    
    if request.method == 'POST':
        # دریافت آیتم‌های تحویل شده از فرم
        delivered_item_ids = request.POST.getlist('delivered_items')
        
        # به‌روزرسانی وضعیت تحویل تمام آیتم‌ها
        for item in invoice.items.all():
            item.is_delivered = str(item.id) in delivered_item_ids
            item.save()
        
        messages.success(request, _('وضعیت تحویل آیتم‌ها با موفقیت به‌روزرسانی شد.'))
    
    return redirect('invoice_detail', pk=pk)


@login_required
def invoice_update_payment(request, pk):
    """به‌روزرسانی وضعیت پرداخت فاکتور"""
    invoice = get_object_or_404(Invoice, pk=pk)
    
    # بررسی دسترسی کاربر به فاکتور
    if not request.user.is_staff and request.user != invoice.booth.manager and request.user not in invoice.booth.staff.all():
        messages.error(request, _('شما اجازه دسترسی به این فاکتور را ندارید.'))
        return redirect('invoice_list')
    
    if request.method == 'POST':
        # دریافت وضعیت پرداخت از فرم
        is_paid = 'is_paid' in request.POST
        payment_method = request.POST.get('payment_method', invoice.payment_method)
        
        # به‌روزرسانی وضعیت پرداخت فاکتور
        invoice.is_paid = is_paid
        invoice.payment_method = payment_method
        
        # پردازش آپلود عکس فیش واریزی (فقط برای پرداخت کارتی)
        if payment_method == 'card' and 'receipt_image' in request.FILES:
            receipt_image = request.FILES['receipt_image']
            # فقط در صورتی که فایل آپلود شده باشد، آن را ذخیره می‌کنیم
            if receipt_image:
                # اگر قبلاً عکسی آپلود شده باشد، آن را حذف می‌کنیم
                if invoice.receipt_image:
                    invoice.receipt_image.delete()
                # ذخیره عکس جدید
                invoice.receipt_image = receipt_image
        
        # اگر روش پرداخت نقدی است و عکس فیش داریم، آن را حذف می‌کنیم
        elif payment_method == 'cash' and invoice.receipt_image:
            invoice.receipt_image.delete()
            invoice.receipt_image = None
        
        invoice.save()
        
        messages.success(request, _('وضعیت پرداخت فاکتور با موفقیت به‌روزرسانی شد.'))
    
    return redirect('invoice_detail', pk=pk)

@login_required
def toggle_all_items_delivery(request, pk):
    """تغییر وضعیت تحویل همه آیتم‌های یک فاکتور"""
    invoice = get_object_or_404(Invoice, pk=pk)
    
    # بررسی دسترسی کاربر به فاکتور
    if not request.user.is_staff and request.user != invoice.booth.manager and request.user not in invoice.booth.staff.all():
        messages.error(request, _('شما اجازه دسترسی به این فاکتور را ندارید.'))
        return redirect('invoice_list')
    
    if request.method == 'POST':
        # دریافت وضعیت جدید تحویل
        set_delivered = request.POST.get('set_delivered') == 'true'
        confirmed = request.POST.get('confirmed') == 'true'
        
        # اگر حالت تحویل نشده است و تأیید نشده، ابتدا باید تأیید شود
        if not set_delivered and not confirmed:
            return JsonResponse({
                'require_confirmation': True,
                'message': _('آیا مطمئن هستید که میخواهید وضعیت تحویل همه محصولات این فاکتور را به تحویل نشده تغییر دهید؟')
            })
        
        # تغییر وضعیت تحویل همه آیتم‌ها
        for item in invoice.items.all():
            item.is_delivered = set_delivered
            item.save()
        
        # انتخاب پیام مناسب برای نمایش
        if set_delivered:
            message = _('وضعیت تحویل همه آیتم‌ها به تحویل شده تغییر یافت.')
        else:
            message = _('وضعیت تحویل همه آیتم‌ها به تحویل نشده تغییر یافت.')
        
        # محاسبه درصد تحویل آیتم‌ها
        delivered_items_count = invoice.items.filter(is_delivered=True).count()
        total_items_count = invoice.items.count()
        delivery_percentage = 0
        if total_items_count > 0:
            delivery_percentage = round((delivered_items_count / total_items_count) * 100)
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': message,
                'all_delivered': set_delivered,
                'delivered_count': delivered_items_count,
                'total_count': total_items_count,
                'delivery_percentage': delivery_percentage
            })
        else:
            messages.success(request, message)
            if 'next' in request.GET:
                return redirect(request.GET.get('next'))
            return redirect('invoice_detail', pk=pk)
    
    # برای درخواست‌های GET، وضعیت فعلی تحویل را بررسی می‌کنیم
    all_delivered = all(item.is_delivered for item in invoice.items.all())
    
    return JsonResponse({
        'success': True,
        'all_delivered': all_delivered
    })

@login_required
def get_booth_products(request, booth_id):
    """API برای گرفتن محصولات یک غرفه - برای استفاده در فرم فاکتور"""
    booth = get_object_or_404(Booth, pk=booth_id)
    
    # بررسی دسترسی کاربر به غرفه
    if not request.user.is_staff and request.user != booth.manager and request.user not in booth.staff.all():
        return JsonResponse({'error': 'دسترسی غیر مجاز'}, status=403)
    
    products = Product.objects.filter(booth=booth, is_available=True).values(
        'id', 'name', 'code', 'price', 'unit__name'
    )
    
    return JsonResponse(list(products), safe=False)

@login_required
def print_invoice(request, pk):
    """چاپ فاکتور"""
    invoice = get_object_or_404(Invoice, pk=pk)
    
    # بررسی دسترسی کاربر به فاکتور
    if not request.user.is_staff and request.user != invoice.booth.manager and request.user != invoice.created_by and request.user not in invoice.booth.staff.all():
        messages.error(request, _('شما اجازه چاپ این فاکتور را ندارید.'))
        return redirect('invoice_detail', pk=invoice.pk)
    
    context = {
        'invoice': invoice,
        'items': invoice.items.all(),
        'title': f'چاپ فاکتور {invoice.invoice_number}'
    }
    return render(request, 'invoices/invoice_print.html', context)

@login_required
def dashboard(request):
    """داشبورد اصلی با آمار فروش کلی"""
    # ایمپورت‌های مورد نیاز
    from django.db.models.functions import TruncDate
    from products.models import Product
    import json
    
    # بررسی دسترسی کاربر به داشبورد
    if not request.user.has_perm('invoices.view_dashboard'):
        messages.error(request, _('شما اجازه دسترسی به داشبورد را ندارید.'))
        return redirect('home')
    
    # آمار کلی فروش
    total_revenue = Invoice.objects.filter(is_paid=True).aggregate(
        total=Sum('total_amount')
    )['total'] or 0
    
    total_donation = Invoice.objects.filter(is_paid=True).aggregate(
        total=Sum('donation_amount')
    )['total'] or 0
    
    invoice_count = Invoice.objects.count()
    
    # فروش به تفکیک غرفه
    booth_data = Booth.objects.annotate(
        sales=Sum('invoices__total_amount'),
        invoice_count=Count('invoices')
    ).filter(invoice_count__gt=0).order_by('-sales')
    
    # آماده سازی داده‌ها برای نمودار غرفه‌ها
    booth_labels = [b.name for b in booth_data]
    booth_sales = [float(b.sales or 0) for b in booth_data]
    
    # فروش روزانه
    daily_data = Invoice.objects.annotate(
        date=TruncDate('created_at')
    ).values('date').annotate(
        total=Sum('total_amount'),
        count=Count('id')
    ).order_by('date')
    
    # وارد کردن jdatetime برای تبدیل تاریخ‌ها به شمسی
    import jdatetime
    
    # تبدیل تاریخ‌های میلادی به شمسی با فرمت سازگار برای نمودار
    date_labels = []
    for item in daily_data:
        gregorian_date = item['date']
        jalali_date = jdatetime.date.fromgregorian(date=gregorian_date)
        date_labels.append(jalali_date.strftime('%Y/%m/%d'))
    
    daily_sales = [float(item['total'] or 0) for item in daily_data]
    
    # اطلاعات آماری برای بخش‌های دیگر داشبورد
    # محاسبه مجموع فروش به تفکیک روش پرداخت (نقدی و کارت)
    cash_sales = Invoice.objects.filter(is_paid=True, payment_method='cash').aggregate(
        total=Sum('total_amount')
    )['total'] or 0
    
    card_sales = Invoice.objects.filter(is_paid=True, payment_method='card').aggregate(
        total=Sum('total_amount')
    )['total'] or 0
    
    stats = {
        'total_sales': total_revenue,
        'invoice_count': invoice_count,
        'total_donation': total_donation,
        'cash_sales': cash_sales,
        'card_sales': card_sales,
    }
    
    # محاسبه پرفروش‌ترین محصولات (5 محصول برتر) - بر اساس تعداد واقعی فروش
    from django.db.models import F
    
    top_products = Product.objects.annotate(
        sold_count=Sum('invoice_items__quantity'),  # جمع کل تعداد محصولات فروخته شده
        invoice_count=Count('invoice_items', distinct=True),  # تعداد فاکتورهایی که این محصول را دارند
        total_sales=Sum(F('invoice_items__quantity') * F('invoice_items__price'))
    ).filter(sold_count__gt=0).order_by('-sold_count')[:5]
    
    # آخرین فاکتورها (5 فاکتور اخیر)
    recent_invoices = Invoice.objects.all().order_by('-created_at')[:5]
    
    context = {
        'stats': stats,
        'booth_data': booth_data,
        'booth_labels': json.dumps(booth_labels),
        'booth_sales': json.dumps(booth_sales),
        'date_labels': json.dumps(date_labels),
        'daily_sales': json.dumps(daily_sales),
        'top_products': top_products,
        'recent_invoices': recent_invoices,
        'title': _('داشبورد')
    }
    return render(request, 'invoices/dashboard.html', context)

@login_required
def dashboard_api(request):
    """API برای گرفتن آمار داشبورد - برای استفاده در نمودارها و به‌روزرسانی خودکار"""
    # ایمپورت‌های مورد نیاز
    from django.db.models.functions import TruncDate
    from products.models import Product
    import jdatetime
    
    # بررسی دسترسی کاربر به داشبورد
    if not request.user.has_perm('invoices.view_dashboard'):
        return JsonResponse({'error': 'دسترسی غیر مجاز'}, status=403)
    
    # آمار کلی فروش
    total_revenue = Invoice.objects.filter(is_paid=True).aggregate(
        total=Sum('total_amount')
    )['total'] or 0
    
    total_donation = Invoice.objects.filter(is_paid=True).aggregate(
        total=Sum('donation_amount')
    )['total'] or 0
    
    invoice_count = Invoice.objects.count()
    
    # محاسبه مجموع فروش به تفکیک روش پرداخت (نقدی و کارت)
    cash_sales = Invoice.objects.filter(is_paid=True, payment_method='cash').aggregate(
        total=Sum('total_amount')
    )['total'] or 0
    
    card_sales = Invoice.objects.filter(is_paid=True, payment_method='card').aggregate(
        total=Sum('total_amount')
    )['total'] or 0
    
    # فروش به تفکیک غرفه
    booth_data = Booth.objects.annotate(
        sales=Sum('invoices__total_amount'),
        invoice_count=Count('invoices')
    ).filter(invoice_count__gt=0).order_by('-sales')
    
    # آماده سازی داده‌ها برای نمودار غرفه‌ها
    booth_labels = [b.name for b in booth_data]
    booth_sales = [float(b.sales or 0) for b in booth_data]
    booth_data_json = [{
        'name': b.name, 
        'sales': float(b.sales or 0),
        'invoice_count': b.invoice_count
    } for b in booth_data]
    
    # فروش روزانه
    daily_data = Invoice.objects.annotate(
        date=TruncDate('created_at')
    ).values('date').annotate(
        total=Sum('total_amount'),
        count=Count('id')
    ).order_by('date')
    
    # تبدیل تاریخ‌های میلادی به شمسی با فرمت سازگار برای نمودار
    date_labels = []
    daily_sales = []
    daily_data_json = []
    
    for item in daily_data:
        gregorian_date = item['date']
        jalali_date = jdatetime.date.fromgregorian(date=gregorian_date)
        jalali_str = jalali_date.strftime('%Y/%m/%d')
        date_labels.append(jalali_str)
        daily_sales.append(float(item['total'] or 0))
        daily_data_json.append({
            'date': jalali_str,
            'total': float(item['total'] or 0),
            'count': item['count']
        })
    
    # محاسبه پرفروش‌ترین محصولات (5 محصول برتر) - بر اساس تعداد واقعی فروش
    top_products = Product.objects.annotate(
        sold_count=Sum('invoice_items__quantity'),  # جمع کل تعداد محصولات فروخته شده
        invoice_count=Count('invoice_items', distinct=True),  # تعداد فاکتورهایی که این محصول را دارند
        total_sales=Sum(F('invoice_items__quantity') * F('invoice_items__price'))
    ).filter(sold_count__gt=0).order_by('-sold_count')[:5]
    
    top_products_json = [{
        'id': p.id,
        'name': p.name,
        'sold_count': int(p.sold_count or 0),
        'invoice_count': p.invoice_count,
        'total_sales': float(p.total_sales or 0)
    } for p in top_products]
    
    # آخرین فاکتورها (5 فاکتور اخیر)
    recent_invoices = Invoice.objects.all().order_by('-created_at')[:5]
    recent_invoices_json = []
    
    for invoice in recent_invoices:
        created_jalali = jdatetime.datetime.fromgregorian(datetime=invoice.created_at)
        recent_invoices_json.append({
            'id': invoice.id,
            'invoice_number': invoice.invoice_number,
            'booth_name': invoice.booth.name,
            'customer_name': invoice.customer_name,
            'total_amount': float(invoice.total_amount),
            'is_paid': invoice.is_paid,
            'created_at': created_jalali.strftime('%Y/%m/%d %H:%M'),
            'items_count': invoice.items.count(),
            'payment_method': invoice.get_payment_method_display(),
            'donation_amount': float(invoice.donation_amount)
        })
    
    # آماده‌سازی آمار نهایی
    stats = {
        'total_sales': float(total_revenue),
        'invoice_count': invoice_count,
        'total_donation': float(total_donation),
        'cash_sales': float(cash_sales),
        'card_sales': float(card_sales),
    }
    
    return JsonResponse({
        'stats': stats,
        'booth_data': booth_data_json,
        'booth_labels': booth_labels,
        'booth_sales': booth_sales,
        'date_labels': date_labels,
        'daily_sales': daily_sales,
        'daily_data': daily_data_json,
        'top_products': top_products_json,
        'recent_invoices': recent_invoices_json
    })


