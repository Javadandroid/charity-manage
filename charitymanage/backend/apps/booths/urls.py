from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BoothViewSet, POSDeviceViewSet

router = DefaultRouter()
router.register(r'pos-devices', POSDeviceViewSet, basename='posdevice')
router.register(r'', BoothViewSet, basename='booth')

urlpatterns = [
    path('', include(router.urls)),
]
