from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.db.models import Sum, Count
from django.http import JsonResponse

from .models import Event
from .forms import EventForm
from booths.models import Booth
from invoices.models import Invoice

# تابع کمکی برای بررسی دسترسی ادمین
def is_admin(user):
    return user.is_staff or user.is_superuser

# Create your views here.

@login_required
@user_passes_test(is_admin, login_url='home')
def event_list(request):
    """نمایش لیست رویدادها - فقط برای ادمین"""
    events = Event.objects.all()
    
    context = {
        'events': events,
        'title': _('رویدادهای خیریه')
    }
    return render(request, 'events/event_list.html', context)

@login_required
@user_passes_test(is_admin, login_url='home')
def event_detail(request, pk):
    """نمایش جزئیات یک رویداد - فقط برای ادمین"""
    event = get_object_or_404(Event, pk=pk)
    
    booths = event.get_active_booths()
    
    # محاسبه آمار رویداد
    stats = {
        'booth_count': booths.count(),
        'total_revenue': event.total_revenue(),
        'invoice_count': Invoice.objects.filter(booth__event=event).count(),
    }
    
    context = {
        'event': event,
        'booths': booths,
        'stats': stats,
        'title': event.name
    }
    return render(request, 'events/event_detail.html', context)

@login_required
@user_passes_test(is_admin, login_url='home')
def event_create(request):
    """ایجاد رویداد جدید - فقط برای ادمین"""
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save()
            messages.success(request, _('رویداد با موفقیت ایجاد شد.'))
            return redirect('event_detail', pk=event.pk)
    else:
        form = EventForm()
    
    context = {
        'form': form,
        'title': _('ایجاد رویداد جدید')
    }
    return render(request, 'events/event_form.html', context)

@login_required
@user_passes_test(is_admin, login_url='home')
def event_update(request, pk):
    """ویرایش رویداد - فقط برای ادمین"""
    event = get_object_or_404(Event, pk=pk)
    
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, _('رویداد با موفقیت بروزرسانی شد.'))
            return redirect('event_detail', pk=event.pk)
    else:
        form = EventForm(instance=event)
    
    context = {
        'form': form,
        'event': event,
        'title': _('ویرایش رویداد')
    }
    return render(request, 'events/event_form.html', context)

@login_required
@user_passes_test(is_admin, login_url='home')
def event_delete(request, pk):
    """حذف رویداد - فقط برای ادمین"""
    event = get_object_or_404(Event, pk=pk)
    
    if request.method == 'POST':
        event.delete()
        messages.success(request, _('رویداد با موفقیت حذف شد.'))
        return redirect('event_list')
    
    context = {
        'event': event,
        'title': _('حذف رویداد')
    }
    return render(request, 'events/event_confirm_delete.html', context)

@login_required
@user_passes_test(is_admin, login_url='home')
def event_dashboard(request, pk):
    """داشبورد آماری رویداد - فقط برای ادمین"""
    event = get_object_or_404(Event, pk=pk)
    
    # محاسبه آمار فروش و همت عالی به تفکیک غرفه
    booths = event.get_active_booths()
    booth_sales = []
    
    for booth in booths:
        booth_stats = {
            'id': booth.id,
            'name': booth.name,
            'sales': booth.total_sales(),
            'donations': booth.total_donations(),
            'invoice_count': Invoice.objects.filter(booth=booth).count(),
        }
        booth_sales.append(booth_stats)
    
    # مرتب‌سازی بر اساس بیشترین فروش
    booth_sales.sort(key=lambda x: x['sales'], reverse=True)
    
    context = {
        'event': event,
        'booth_sales': booth_sales,
        'total_revenue': event.total_revenue(),
        'total_donations': event.total_donations(),
        'title': _('داشبورد رویداد {0}').format(event.name)
    }
    return render(request, 'events/event_dashboard.html', context)

@login_required
@user_passes_test(is_admin, login_url='home')
def event_stats_api(request, pk):
    """API برای گرفتن آمار رویداد - برای استفاده در نمودارها - فقط برای ادمین"""
    event = get_object_or_404(Event, pk=pk)
    
    # آمار فروش به تفکیک غرفه
    booth_sales = Booth.objects.filter(event=event).annotate(
        total=Sum('invoices__total_amount'),
        count=Count('invoices')
    ).values('name', 'total', 'count')
    
    return JsonResponse({
        'booth_sales': list(booth_sales),
        'event_name': event.name
    })
