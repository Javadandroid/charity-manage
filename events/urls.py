from django.urls import path
from . import views

urlpatterns = [
    path('', views.event_list, name='event_list'),
    path('<int:pk>/', views.event_detail, name='event_detail'),
    path('create/', views.event_create, name='event_create'),
    path('<int:pk>/update/', views.event_update, name='event_update'),
    path('<int:pk>/delete/', views.event_delete, name='event_delete'),
    path('<int:pk>/dashboard/', views.event_dashboard, name='event_dashboard'),
    path('<int:pk>/stats/api/', views.event_stats_api, name='event_stats_api'),
]
