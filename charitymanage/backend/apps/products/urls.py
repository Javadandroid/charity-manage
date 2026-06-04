from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UnitOfMeasureViewSet, ProductViewSet

router = DefaultRouter()
router.register(r'units', UnitOfMeasureViewSet)
router.register(r'products', ProductViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
