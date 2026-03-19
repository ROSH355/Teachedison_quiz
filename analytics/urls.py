from django.urls import path
from . import views

urlpatterns = [
    path('performance/', views.performance_view, name='analytics-performance'),
    path('history/', views.history_view, name='analytics-history'),
]