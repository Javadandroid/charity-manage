from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FontViewSet, SystemSettingView

router = DefaultRouter()
router.register(r'fonts', FontViewSet)

urlpatterns = [
    path('settings/', SystemSettingView.as_view(), name='settings'),
    path('', include(router.urls)),
]
