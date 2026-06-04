from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse
from django.db.models import Sum, F
import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter
import jdatetime

from invoices.models import Invoice, InvoiceItem
from booths.models import Booth
from products.models import Product

# تابع کمکی برای بررسی دسترسی کاربر (همان تابع قبلی از charity_event_manager.views)
# اگر این تابع در جای دیگری از پروژه هم استفاده می‌شود، بهتر است آن را به یک فایل utils منتقل کنید.
def is_admin_or_ershad(user):
    """چک کردن اینکه آیا کاربر ادمین است یا نام کاربری ershad دارد"""
    return user.is_staff or user.username == 'ershad'


@login_required
@user_passes_test(is_admin_or_ershad, login_url='home')
def generate_market_report(request):
    """تولید گزارش اکسل از فروش بازارچه"""
    wb = openpyxl.Workbook()

    # استایل‌های مختلف برای سلول‌ها
    header_font = Font(name='Estedad Regular', size=12, bold=True)
    normal_font = Font(name='Estedad Regular', size=11)
    header_fill = PatternFill(start_color='DDEBF7', end_color='DDEBF7', fill_type='solid')
    thin_border_side = Side(style='thin')
    border = Border(
        left=thin_border_side,
        right=thin_border_side,
        top=thin_border_side,
        bottom=thin_border_side
    )
    center_alignment = Alignment(horizontal='center', vertical='center')
    number_format_thousands = '#,##0'

    # --- شیت اول: فروش کل ---
    ws1 = wb.active
    ws1.title = "فروش کل"
    ws1.sheet_view.rightToLeft = True

    # تنظیم عرض ستون‌ها
    column_widths_ws1 = {'A': 5, 'B': 18, 'C': 25, 'D': 15, 'E': 10, 'F': 18, 'G': 15, 'H': 20}
    for col_letter, width in column_widths_ws1.items():
        ws1.column_dimensions[col_letter].width = width

    # سربرگ جدول
    headers_ws1 = ['ردیف', 'تاریخ', 'نام کالا', 'قیمت واحد', 'تعداد', 'قیمت کل', 'شماره فاکتور', 'غرفه']
    for col_num, header_title in enumerate(headers_ws1, 1):
        cell = ws1.cell(row=1, column=col_num, value=header_title)
        cell.font = header_font
        cell.fill = header_fill
        cell.border = border
        cell.alignment = center_alignment

    # داده‌های فروش
    invoice_items = InvoiceItem.objects.select_related('invoice', 'product', 'invoice__booth').order_by('invoice__created_at')

    for row_idx, item in enumerate(invoice_items, 1):
        jalali_datetime = jdatetime.datetime.fromgregorian(datetime=item.invoice.created_at)
        jalali_date_str = jalali_datetime.strftime('%Y/%m/%d %H:%M')

        row_data = [
            row_idx,
            jalali_date_str,
            item.product.name,
            item.price,
            item.quantity,
            item.price * item.quantity,
            item.invoice.invoice_number,
            item.invoice.booth.name,
        ]

        for col_idx, cell_value in enumerate(row_data, 1):
            cell = ws1.cell(row=row_idx + 1, column=col_idx, value=cell_value)
            cell.font = normal_font
            cell.border = border
            cell.alignment = center_alignment
            if col_idx in [4, 6]: # قیمت واحد و قیمت کل
                cell.number_format = number_format_thousands

    # --- شیت دوم: فروش روزانه ---
    ws2 = wb.create_sheet(title="فروش روزانه")
    ws2.sheet_view.rightToLeft = True

    # بدست آوردن روزهای فروش و غرفه‌ها
    all_invoices = Invoice.objects.all().order_by('created_at')
    jalali_dates_for_header = []
    for inv in all_invoices:
        j_date = jdatetime.date.fromgregorian(date=inv.created_at.date())
        jalali_dates_for_header.append(j_date.strftime('%Y/%m/%d'))

    unique_jalali_dates = sorted(list(set(jalali_dates_for_header)))
    all_booths = Booth.objects.all().order_by('name')

    # تنظیم عرض ستون‌ها
    ws2.column_dimensions['A'].width = 25
    for i, _ in enumerate(unique_jalali_dates):
        col_letter = get_column_letter(i + 2)
        ws2.column_dimensions[col_letter].width = 15
    ws2.column_dimensions[get_column_letter(len(unique_jalali_dates) + 2)].width = 18 # ستون فروش کل

    # سربرگ جدول با تاریخ‌های شمسی
    headers_ws2 = ['نام غرفه'] + unique_jalali_dates + ['فروش کل']
    for col_num, header_title in enumerate(headers_ws2, 1):
        cell = ws2.cell(row=1, column=col_num, value=header_title)
        cell.font = header_font
        cell.fill = header_fill
        cell.border = border
        cell.alignment = center_alignment

    # محاسبه فروش روزانه هر غرفه
    current_row_num_ws2 = 2
    grand_total_sales = 0
    daily_totals_for_footer = {date_str: 0 for date_str in unique_jalali_dates}

    for booth_obj in all_booths:
        cell_booth_name = ws2.cell(row=current_row_num_ws2, column=1, value=booth_obj.name)
        cell_booth_name.font = normal_font
        cell_booth_name.border = border
        cell_booth_name.alignment = center_alignment

        total_booth_sales_for_row = 0
        for col_idx, date_str in enumerate(unique_jalali_dates, 2):
            date_parts = date_str.split('/')
            j_date_obj = jdatetime.date(int(date_parts[0]), int(date_parts[1]), int(date_parts[2]))
            g_date_obj = j_date_obj.togregorian()

            daily_sales_for_booth = Invoice.objects.filter(
                booth_id=booth_obj.id,
                created_at__date=g_date_obj
            ).aggregate(total_sales=Sum(F('total_amount')))['total_sales'] or 0

            cell = ws2.cell(row=current_row_num_ws2, column=col_idx, value=daily_sales_for_booth)
            cell.font = normal_font
            cell.border = border
            cell.alignment = center_alignment
            cell.number_format = number_format_thousands

            total_booth_sales_for_row += daily_sales_for_booth
            daily_totals_for_footer[date_str] += daily_sales_for_booth

        # فروش کل غرفه در ردیف
        cell_total_booth_sales = ws2.cell(row=current_row_num_ws2, column=len(unique_jalali_dates) + 2, value=total_booth_sales_for_row)
        cell_total_booth_sales.font = Font(name='Estedad Regular', size=11, bold=True)
        cell_total_booth_sales.border = border
        cell_total_booth_sales.alignment = center_alignment
        cell_total_booth_sales.fill = PatternFill(start_color='FFEBF5', end_color='FFEBF5', fill_type='solid')
        cell_total_booth_sales.number_format = number_format_thousands
        grand_total_sales += total_booth_sales_for_row
        current_row_num_ws2 += 1

    # ردیف جمع کل فروش روزانه (فوتر)
    footer_row_num = current_row_num_ws2
    cell_footer_label = ws2.cell(row=footer_row_num, column=1, value="جمع کل فروش")
    cell_footer_label.font = header_font
    cell_footer_label.border = border
    cell_footer_label.alignment = center_alignment
    cell_footer_label.fill = PatternFill(start_color='FFEBF5', end_color='FFEBF5', fill_type='solid')

    for col_idx, date_str in enumerate(unique_jalali_dates, 2):
        cell_daily_total = ws2.cell(row=footer_row_num, column=col_idx, value=daily_totals_for_footer[date_str])
        cell_daily_total.font = Font(name='Estedad Regular', size=11, bold=True)
        cell_daily_total.border = border
        cell_daily_total.alignment = center_alignment
        cell_daily_total.fill = PatternFill(start_color='FFEBF5', end_color='FFEBF5', fill_type='solid')
        cell_daily_total.number_format = number_format_thousands

    # جمع کل فروش (گوشه پایین سمت راست)
    cell_grand_total = ws2.cell(row=footer_row_num, column=len(unique_jalali_dates) + 2, value=grand_total_sales)
    cell_grand_total.font = Font(name='Estedad Regular', size=12, bold=True)
    cell_grand_total.border = border
    cell_grand_total.alignment = center_alignment
    cell_grand_total.fill = PatternFill(start_color='FFEBF5', end_color='FFEBF5', fill_type='solid')
    cell_grand_total.number_format = number_format_thousands

    # تولید فایل اکسل و ارسال پاسخ
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=market_report.xlsx'
    wb.save(response)
    return response


@login_required
@user_passes_test(is_admin_or_ershad, login_url='home')
def generate_product_sales_report(request):
    """تولید گزارش اکسل از فروش محصولات."""
    wb = openpyxl.Workbook()

    # استایل‌های مختلف برای سلول‌ها (مشابه گزارش بازارچه)
    header_font = Font(name='Estedad Regular', size=12, bold=True)
    normal_font = Font(name='Estedad Regular', size=11)
    header_fill = PatternFill(start_color='DDEBF7', end_color='DDEBF7', fill_type='solid')
    thin_border_side = Side(style='thin')
    border = Border(
        left=thin_border_side,
        right=thin_border_side,
        top=thin_border_side,
        bottom=thin_border_side
    )
    center_alignment = Alignment(horizontal='center', vertical='center')
    right_alignment = Alignment(horizontal='right', vertical='center') # برای نام محصول و غرفه
    number_format_thousands = '#,##0'

    ws = wb.active
    ws.title = "فروش محصولات"
    ws.sheet_view.rightToLeft = True

    # تنظیم عرض ستون‌ها
    column_widths = {'A': 5, 'B': 40, 'C': 15, 'D': 18, 'E': 25} # ردیف، نام محصول، تعداد فروش، قیمت، غرفه
    for col_letter, width in column_widths.items():
        ws.column_dimensions[col_letter].width = width

    # سربرگ جدول
    headers = ['ردیف', 'نام محصول', 'تعداد فروش', 'قیمت واحد', 'غرفه']
    for col_num, header_title in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col_num, value=header_title)
        cell.font = header_font
        cell.fill = header_fill
        cell.border = border
        cell.alignment = center_alignment

    # داده‌های محصولات
    products = Product.objects.select_related('booth', 'unit').all().order_by('booth__name', 'name')

    row_idx = 1
    for product_item in products:
        row_idx += 1 # شروع از ردیف دوم برای داده‌ها
        
        total_sold = product_item.invoice_items.aggregate(sold_quantity=Sum('quantity'))['sold_quantity'] or 0
        
        unit_name = f" ({product_item.unit.name})" if product_item.unit else ""
        product_name_with_unit = f"{product_item.name}{unit_name}"

        row_data = [
            row_idx -1, # شماره ردیف
            product_name_with_unit,
            total_sold,
            product_item.price,
            product_item.booth.name if product_item.booth else "نامشخص",
        ]

        for col_idx, cell_value in enumerate(row_data, 1):
            cell = ws.cell(row=row_idx, column=col_idx, value=cell_value)
            cell.font = normal_font
            cell.border = border
            # تنظیم ترازبندی
            if col_idx in [1, 3, 4]: # ردیف، تعداد، قیمت
                cell.alignment = center_alignment
            else: # نام محصول، غرفه
                cell.alignment = right_alignment
            
            if col_idx == 4: # قیمت
                cell.number_format = number_format_thousands
            elif col_idx == 3: # تعداد فروش
                cell.number_format = '0'

    # تولید فایل اکسل و ارسال پاسخ
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="product_sales_report.xlsx"'
    wb.save(response)
    return response


def normalize_phone(phone_str):
    if not phone_str:
        return ""
    persian_to_english = {
        '۰': '0', '۱': '1', '۲': '2', '۳': '3', '۴': '4',
        '۵': '5', '۶': '6', '۷': '7', '۸': '8', '۹': '9',
        '٠': '0', '١': '1', '٢': '2', '٣': '3', '٤': '4',
        '٥': '5', '٦': '6', '٧': '7', '٨': '8', '٩': '9',
    }
    cleaned = "".join(persian_to_english.get(char, char) for char in str(phone_str))
    cleaned = "".join(c for c in cleaned if c.isdigit())
    if len(cleaned) == 10 and cleaned.startswith('9'):
        cleaned = '0' + cleaned
    return cleaned


def consolidate_names(names_set):
    names = list(names_set)
    cleaned_names = [n for n in names if n not in ["بدون نام", "کیوسک", ""]]
    if cleaned_names:
        return " / ".join(cleaned_names)
    elif names:
        non_empty = [n for n in names if n]
        if non_empty:
            return " / ".join(non_empty)
    return "بدون نام"


@login_required
@user_passes_test(is_admin_or_ershad, login_url='home')
def generate_customer_phones_report(request):
    """تولید گزارش اکسل از شماره تماس مشتریان."""
    invoices = Invoice.objects.exclude(customer_phone='').exclude(customer_phone__isnull=True)
    
    customers = {}
    for inv in invoices:
        phone = normalize_phone(inv.customer_phone)
        if not phone:
            continue
        
        if phone not in customers:
            customers[phone] = {
                'names': set(),
                'invoice_numbers': [],
                'total_amount': 0
            }
        
        name = inv.customer_name.strip() if inv.customer_name else ""
        if name:
            customers[phone]['names'].add(name)
        
        # استخراج بخش عددی شماره فاکتور
        inv_num_raw = inv.invoice_number
        inv_num_clean = "".join(c for c in inv_num_raw if c.isdigit())
        if inv_num_clean:
            inv_num_display = str(int(inv_num_clean))
        else:
            inv_num_display = inv_num_raw
            
        customers[phone]['invoice_numbers'].append(inv_num_display)
        customers[phone]['total_amount'] += inv.total_amount
        
    rows = []
    for phone, data in customers.items():
        name = consolidate_names(data['names'])
        try:
            sorted_inv_nums = sorted(data['invoice_numbers'], key=int)
        except ValueError:
            sorted_inv_nums = sorted(data['invoice_numbers'])
        invoice_nums_str = ", ".join(sorted_inv_nums)
        
        rows.append({
            'phone': phone,
            'name': name,
            'invoice_numbers': invoice_nums_str,
            'total_amount': data['total_amount']
        })
        
    # مرتب‌سازی بر اساس مبلغ کل خرید از زیاد به کم
    rows.sort(key=lambda x: x['total_amount'], reverse=True)
    
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "شماره تماس مشتریان"
    ws.sheet_view.rightToLeft = True
    
    # تنظیم عرض ستون‌ها
    column_widths = {'A': 8, 'B': 25, 'C': 18, 'D': 35, 'E': 20}
    for col_letter, width in column_widths.items():
        ws.column_dimensions[col_letter].width = width
        
    # استایل‌های سلول‌ها (همانند گزارش‌های قبلی برنامه)
    header_font = Font(name='Estedad Regular', size=12, bold=True)
    normal_font = Font(name='Estedad Regular', size=11)
    header_fill = PatternFill(start_color='DDEBF7', end_color='DDEBF7', fill_type='solid')
    thin_border_side = Side(style='thin')
    border = Border(
        left=thin_border_side,
        right=thin_border_side,
        top=thin_border_side,
        bottom=thin_border_side
    )
    center_alignment = Alignment(horizontal='center', vertical='center')
    right_alignment = Alignment(horizontal='right', vertical='center')
    number_format_thousands = '#,##0'
    
    # سربرگ جدول
    headers = ['ردیف', 'نام', 'شماره', 'شماره‌های فاکتور', 'مبلغ کل خرید']
    for col_num, header_title in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col_num, value=header_title)
        cell.font = header_font
        cell.fill = header_fill
        cell.border = border
        cell.alignment = center_alignment
        
    # درج داده‌ها در اکسل
    for idx, row_data in enumerate(rows, 1):
        row_idx = idx + 1
        
        ws.cell(row=row_idx, column=1, value=idx)  # ردیف
        ws.cell(row=row_idx, column=2, value=row_data['name'])  # نام
        ws.cell(row=row_idx, column=3, value=row_data['phone'])  # شماره
        ws.cell(row=row_idx, column=4, value=row_data['invoice_numbers'])  # شماره‌های فاکتور
        ws.cell(row=row_idx, column=5, value=row_data['total_amount'])  # مبلغ کل خرید
        
        for col_idx in range(1, 6):
            cell = ws.cell(row=row_idx, column=col_idx)
            cell.font = normal_font
            cell.border = border
            
            # ترازبندی
            if col_idx in [1, 3, 4, 5]:  # ردیف، شماره، شماره‌های فاکتور، مبلغ
                cell.alignment = center_alignment
            else:  # نام
                cell.alignment = right_alignment
                
            # فرمت هزینه‌ها
            if col_idx == 5:
                cell.number_format = number_format_thousands
            elif col_idx == 3:
                cell.number_format = '@'
                
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="customer_phones_report.xlsx"'
    wb.save(response)
    return response


@login_required
@user_passes_test(is_admin_or_ershad, login_url='home')
def report_index(request):
    """صفحه اصلی بخش گزارشات."""
    context = {
        'title': 'بخش گزارشات',
    }
    return render(request, 'reports/report_index.html', context)
