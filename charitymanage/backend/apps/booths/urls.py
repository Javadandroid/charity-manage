from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BoothViewSet, POSDeviceViewSet

router = DefaultRouter()
router.register(r'booths', BoothViewSet)
router.register(r'pos-devices', POSDeviceViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
