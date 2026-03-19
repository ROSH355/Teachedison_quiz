from django.urls import path
from . import views

urlpatterns = [
    path('start/', views.start_attempt_view, name='attempt-start'),
    path('history/', views.attempt_history_view, name='attempt-history'),
    path('<int:attempt_id>/submit/', views.submit_attempt_view, name='attempt-submit'),
    path('<int:attempt_id>/result/', views.attempt_result_view, name='attempt-result'),
]