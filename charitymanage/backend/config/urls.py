from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/core/', include('apps.core.urls')),
    path('api/events/', include('apps.events.urls')),
    path('api/booths/', include('apps.booths.urls')),
    path('api/products/', include('apps.products.urls')),
    path('api/invoices/', include('apps.invoices.urls')),
    path('api/reports/', include('apps.reports.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
