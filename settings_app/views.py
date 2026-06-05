from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.http import HttpResponse
import os

from .models import Font, SystemSetting
from .forms import FontForm, SystemSettingForm

@login_required
def settings_dashboard(request):
    """صفحه داشبورد تنظیمات"""
    # فقط ادمین‌ها اجازه دسترسی دارند
    if not request.user.is_staff:
        messages.error(request, _('شما اجازه دسترسی به این صفحه را ندارید.'))
        return redirect('home')
    
    settings = SystemSetting.get_settings()
    fonts = Font.objects.all().order_by('-is_active', 'name')
    
    context = {
        'settings': settings,
        'fonts': fonts,
        'title': _('تنظیمات سیستم')
    }
    return render(request, 'settings_app/settings_dashboard.html', context)

@login_required
def font_list(request):
    """لیست فونت‌های سیستم"""
    # فقط ادمین‌ها اجازه دسترسی دارند
    if not request.user.is_staff:
        messages.error(request, _('شما اجازه دسترسی به این صفحه را ندارید.'))
        return redirect('home')
    
    fonts = Font.objects.all().order_by('-is_active', 'name')
    
    context = {
        'fonts': fonts,
        'title': _('مدیریت فونت‌ها')
    }
    return render(request, 'settings_app/font_list.html', context)

@login_required
def font_create(request):
    """افزودن فونت جدید"""
    # فقط ادمین‌ها اجازه دسترسی دارند
    if not request.user.is_staff:
        messages.error(request, _('شما اجازه دسترسی به این صفحه را ندارید.'))
        return redirect('home')
    
    if request.method == 'POST':
        form = FontForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, _('فونت جدید با موفقیت اضافه شد.'))
            return redirect('font_list')
    else:
        form = FontForm()
    
    context = {
        'form': form,
        'title': _('افزودن فونت جدید')
    }
    return render(request, 'settings_app/font_form.html', context)

@login_required
def font_update(request, pk):
    """ویرایش فونت"""
    # فقط ادمین‌ها اجازه دسترسی دارند
    if not request.user.is_staff:
        messages.error(request, _('شما اجازه دسترسی به این صفحه را ندارید.'))
        return redirect('home')
    
    font = get_object_or_404(Font, pk=pk)
    
    if request.method == 'POST':
        form = FontForm(request.POST, request.FILES, instance=font)
        if form.is_valid():
            form.save()
            messages.success(request, _('فونت با موفقیت بروزرسانی شد.'))
            return redirect('font_list')
    else:
        form = FontForm(instance=font)
    
    context = {
        'form': form,
        'font': font,
        'title': _('ویرایش فونت')
    }
    return render(request, 'settings_app/font_form.html', context)

@login_required
def font_delete(request, pk):
    """حذف فونت"""
    # فقط ادمین‌ها اجازه دسترسی دارند
    if not request.user.is_staff:
        messages.error(request, _('شما اجازه دسترسی به این صفحه را ندارید.'))
        return redirect('home')
    
    font = get_object_or_404(Font, pk=pk)
    
    # اگر فونت در تنظیمات سیستم استفاده شده باشد، اجازه حذف ندهید
    settings = SystemSetting.get_settings()
    if settings.primary_font == font:
        messages.error(request, _('این فونت در تنظیمات سیستم استفاده شده است و قابل حذف نیست.'))
        return redirect('font_list')
    
    if request.method == 'POST':
        # حذف فایل فونت از سیستم فایل
        if font.font_file and os.path.isfile(font.font_file.path):
            os.remove(font.font_file.path)
        
        font.delete()
        messages.success(request, _('فونت با موفقیت حذف شد.'))
        return redirect('font_list')
    
    context = {
        'font': font,
        'title': _('حذف فونت')
    }
    return render(request, 'settings_app/font_confirm_delete.html', context)

@login_required
def system_settings(request):
    """تنظیمات سیستم"""
    # فقط ادمین‌ها اجازه دسترسی دارند
    if not request.user.is_staff:
        messages.error(request, _('شما اجازه دسترسی به این صفحه را ندارید.'))
        return redirect('home')
    
    settings = SystemSetting.get_settings()
    
    if request.method == 'POST':
        form = SystemSettingForm(request.POST, request.FILES, instance=settings)
        if form.is_valid():
            form.save()
            messages.success(request, _('تنظیمات سیستم با موفقیت بروزرسانی شد.'))
            return redirect('settings_dashboard')
    else:
        form = SystemSettingForm(instance=settings)
    
    context = {
        'form': form,
        'settings': settings,
        'title': _('ویرایش تنظیمات سیستم')
    }
    return render(request, 'settings_app/system_settings_form.html', context)

@login_required
def generate_font_css(request):
    """تولید CSS برای فونت‌های سیستم"""
    settings = SystemSetting.get_settings()
    fonts = Font.objects.filter(is_active=True)
    
    response = HttpResponse(content_type='text/css')
    response['Content-Disposition'] = 'inline; filename="custom-fonts.css"'
    
    # تولید CSS برای هر فونت
    for font in fonts:
        font_url = font.font_file.url
        font_format = 'woff' if font_url.lower().endswith('.woff') else 'truetype'
        
        css = f'''
/* Font: {font.name} */
@font-face {{
    font-family: '{font.name}';
    src: url('{font_url}') format('{font_format}');
    font-weight: normal;
    font-style: normal;
}}
'''
        response.write(css)
    
    # اگر فونت اصلی تنظیم شده باشد، آن را به عنوان فونت اصلی تنظیم کن
    if settings.primary_font:
        css = f'''
/* Use primary font for the whole site */
body, html, .font-primary {{
    font-family: '{settings.primary_font.name}', 'Vazir', 'Tahoma', sans-serif !important;
}}
'''
        response.write(css)
    
    # تنظیمات رنگ سیستم
    colors_css = f'''
/* System colors */
:root {{
    --primary-color: {settings.primary_color};
    --secondary-color: {settings.secondary_color};
}}

.bg-primary {{
    background-color: var(--primary-color) !important;
}}

.bg-secondary {{
    background-color: var(--secondary-color) !important;
}}

.btn-primary {{
    background-color: var(--primary-color) !important;
    border-color: var(--primary-color) !important;
}}

.btn-secondary {{
    background-color: var(--secondary-color) !important;
    border-color: var(--secondary-color) !important;
}}
'''
    response.write(colors_css)
    
    return response
