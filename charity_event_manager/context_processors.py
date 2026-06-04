from django.conf import settings

def app_settings(request):
    return {
        'KIOSK_REDIRECT_SECONDS': getattr(settings, 'KIOSK_REDIRECT_SECONDS', 20),
        'INVOICE_LIST_POLL_SECONDS': getattr(settings, 'INVOICE_LIST_POLL_SECONDS', 10),
        'DASHBOARD_REFRESH_INTERVAL': getattr(settings, 'DASHBOARD_REFRESH_INTERVAL', 10),
    }
