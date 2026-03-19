from django.contrib import admin
from .models import UserAnalytics


@admin.register(UserAnalytics)
class UserAnalyticsAdmin(admin.ModelAdmin):
    list_display = ['user', 'total_attempts', 'average_score',
                    'highest_score', 'accuracy_percentage', 'last_attempt_at']
    readonly_fields = ['accuracy_percentage']