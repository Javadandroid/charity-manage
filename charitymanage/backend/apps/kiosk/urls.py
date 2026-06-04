from django.urls import path
from .views import GenerateTTSView

urlpatterns = [
    path('tts/', GenerateTTSView.as_view(), name='generate-tts'),
]
