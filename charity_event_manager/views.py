from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.db.models import Sum, Count # F و HttpResponse و collections و numbers و openpyxl.styles.numbers حذف شدند
from django.http import JsonResponse, HttpResponseForbidden
from django.core.cache import cache
from django.conf import settings
import os
from datetime import datetime
import subprocess
import shutil
from events.models import Event
from invoices.models import Invoice
from booths.models import Booth

def home(request):
    """صفحه اصلی سایت"""
    # نمایش رویدادهای فعال
    active_events = Event.objects.filter(is_active=True)
    
    context = {
        'events': active_events,
        'title': _('سیستم مدیریت رویدادهای خیریه')
    }
    return render(request, 'home.html', context)

@login_required
def user_dashboard(request):
    """داشبورد کاربر"""
    # غرفه‌های مدیریت شده توسط کاربر
    managed_booths = Booth.objects.filter(manager=request.user)
    
    # غرفه‌هایی که کاربر در آن‌ها کارمند است
    staff_booths = Booth.objects.filter(staff=request.user)
    
    # فاکتورهایی که توسط کاربر ایجاد شده‌اند
    invoices = Invoice.objects.filter(created_by=request.user).order_by('-created_at')[:10]
    
    # آمار فروش کاربر
    sales_stats = Invoice.objects.filter(created_by=request.user).aggregate(
        total=Sum('total_amount'),
        count=Count('id')
    )
    
    context = {
        'managed_booths': managed_booths,
        'staff_booths': staff_booths,
        'invoices': invoices,
        'sales_stats': sales_stats,
        'title': _('داشبورد من') # Corrected
    }
    return render(request, 'user_dashboard.html', context) # Corrected

def user_login(request):
    """ورود کاربر"""
    if request.user.is_authenticated: # Added back
        return redirect('user_dashboard')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, _('با موفقیت وارد شدید.')) # Corrected
                
                # هدایت به صفحه‌ای که کاربر قبل از ورود می‌خواسته به آن برود (Added back)
                next_page = request.GET.get('next')
                if next_page:
                    return redirect(next_page)
                return redirect('user_dashboard')
            else:
                messages.error(request, _('نام کاربری یا رمز عبور نامعتبر است.')) # Kept from current, which is same as original for this case
        else:
            # نمایش خطاها در فرم (Kept current detailed error reporting)
            error_messages = []
            for field, errors in form.errors.items():
                for error in errors:
                    error_messages.append(f"{form.fields[field].label if field != '__all__' else ''}: {error}")
            messages.error(request, "\n".join(error_messages))
            
    else:
        form = AuthenticationForm()
    
    context = {
        'form': form,
        'title': _('ورود به سیستم')
    }
    return render(request, 'login.html', context)

def user_logout(request):
    """خروج کاربر"""
    logout(request)
    messages.success(request, _('با موفقیت خارج شدید.'))
    return redirect('home')

@login_required
def nobat_page(request):
    """صفحه نمایش نوبت (تمام‌صفحه اختیاری)"""
    # فقط ادمین یا ادمینِ غرفه/کارکنان اجازه ببینند
    allowed = request.user.is_staff or request.user.groups.filter(name='ادمین غرفه').exists()
    if not allowed:
        # اگر کاربر در هیچ غرفه‌ای مدیر/کارمند نیست، منع دسترسی
        is_booth_user = Booth.objects.filter(manager=request.user).exists() or Booth.objects.filter(staff=request.user).exists()
        if not is_booth_user:
            return HttpResponseForbidden(_('اجازه دسترسی ندارید.'))
    data = cache.get('nobat_current', {}) or {}
    context = {
        'title': _('نوبت'),
        'current': data,
    }
    return render(request, 'nobat.html', context)

@login_required
def nobat_current(request):
    """API: گرفتن نوبت فعلی برای نمایش"""
    data = cache.get('nobat_current', {}) or {}
    return JsonResponse({'ok': True, 'data': data})

@login_required
def nobat_show(request):
    """API: تنظیم نوبت فعلی بر اساس فاکتور انتخاب‌شده"""
    if request.method != 'POST':
        return JsonResponse({'ok': False, 'message': 'Invalid method'}, status=405)
    try:
        invoice_id = int(request.POST.get('invoice_id') or 0)
    except ValueError:
        invoice_id = 0
    if not invoice_id:
        return JsonResponse({'ok': False, 'message': 'invoice_id required'}, status=400)
    inv = get_object_or_404(Invoice, pk=invoice_id)
    # مجوز: ادمین یا مدیر/کارمند همان غرفه
    if not (request.user.is_staff or inv.booth.manager_id == request.user.id or inv.booth.staff.filter(id=request.user.id).exists()):
        return JsonResponse({'ok': False, 'message': 'forbidden'}, status=403)
    # محاسبه شماره قابل نمایش: حذف inv و صفرهای پیشرو
    disp = inv.invoice_number or ''
    try:
        if disp.lower().startswith('inv'):
            disp = disp[3:]
        disp = str(int(disp))
    except Exception:
        pass
    payload = {
        'invoice_id': inv.id,
        'display_number': disp,
        'booth_name': inv.booth.name,
    }
    payload['tts_backend'] = 'none'
    tts_error = None
    # Diagnostics
    try:
        payload['backend_setting'] = getattr(settings, 'NOBAT_TTS_BACKEND', 'browser')
        payload['media_root_set'] = bool(getattr(settings, 'MEDIA_ROOT', None))
        payload['espeak_path'] = shutil.which('espeak-ng') or shutil.which('espeak') or ''
        payload['ffmpeg_path'] = shutil.which('ffmpeg') or ''
    except Exception:
        pass
    # تولید صوت سروری بر اساس بک‌اند انتخاب‌شده
    try:
        backend = getattr(settings, 'NOBAT_TTS_BACKEND', 'browser')
        if getattr(settings, 'NOBAT_TTS_ENABLED', True) and backend == 'espeak':
            # متن فارسی با رقم‌های فارسی برای خواندن بهتر
            def _to_fa_digits(s: str) -> str:
                m = {'0':'۰','1':'۱','2':'۲','3':'۳','4':'۴','5':'۵','6':'۶','7':'۷','8':'۸','9':'۹'}
                return ''.join(m.get(ch, ch) for ch in str(s))
            text = f"شماره {_to_fa_digits(disp)}. غرفه {inv.booth.name}"
            base_dir = getattr(settings, 'MEDIA_ROOT', None)
            base_url = getattr(settings, 'MEDIA_URL', '/media/')
            if base_dir:
                out_dir = os.path.join(base_dir, 'nobat')
                os.makedirs(out_dir, exist_ok=True)
                # پاک‌سازی اختیاری
                try:
                    days = int(getattr(settings, 'NOBAT_TTS_CLEANUP_DAYS', 0) or 0)
                    if days > 0:
                        cutoff = datetime.now().timestamp() - days*24*3600
                        for fn in os.listdir(out_dir):
                            fp = os.path.join(out_dir, fn)
                            try:
                                if os.path.getmtime(fp) < cutoff:
                                    os.remove(fp)
                            except Exception:
                                pass
                except Exception:
                    pass
                ts = datetime.now().strftime('%Y%m%d%H%M%S')
                wav_name = f"nobat_{inv.id}_{ts}.wav"
                wav_path = os.path.join(out_dir, wav_name)
                voice = getattr(settings, 'NOBAT_TTS_ESPEAK_VOICE', 'fa')
                rate = int(getattr(settings, 'NOBAT_TTS_ESPEAK_RATE', 150))
                # پیدا کردن دستور espeak-ng یا espeak
                exe = shutil.which('espeak-ng') or shutil.which('espeak')
                if not exe:
                    raise RuntimeError('espeak-ng/espeak not found on system PATH')
                # ساخت فایل WAV
                cmd = [exe, '-v', voice, '-s', str(rate), '-w', wav_path, text]
                try:
                    subprocess.run(cmd, check=True)
                except subprocess.CalledProcessError as e:
                    raise RuntimeError(f'espeak failed: {e}')
                audio_rel_url = f"{base_url.rstrip('/')}/nobat/{wav_name}"
                # تبدیل به MP3 اگر ffmpeg موجود و اجازه داده شده
                if getattr(settings, 'NOBAT_TTS_USE_FFMPEG', True) and shutil.which('ffmpeg'):
                    mp3_name = wav_name[:-4] + '.mp3'
                    mp3_path = os.path.join(out_dir, mp3_name)
                    try:
                        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', wav_path, mp3_path], check=True)
                        audio_rel_url = f"{base_url.rstrip('/')}/nobat/{mp3_name}"
                    except subprocess.CalledProcessError as e:
                        # اگر تبدیل شکست خورد همان WAV را استفاده می‌کنیم
                        pass
                payload['audio_url'] = audio_rel_url
                payload['tts_backend'] = 'espeak'
    except Exception as e:
        tts_error = str(e)
    cache.set('nobat_current', payload, timeout=60*60*12)  # 12h
    if tts_error:
        payload['tts_error'] = tts_error
    return JsonResponse({'ok': True, 'data': payload})
