from rest_framework import serializers
from .models import UserAnalytics


class UserAnalyticsSerializer(serializers.ModelSerializer):
    accuracy_percentage = serializers.ReadOnlyField()
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_name = serializers.CharField(source='user.full_name', read_only=True)

    class Meta:
        model = UserAnalytics
        fields = [
            'user_email', 'user_name',
            'total_attempts', 'completed_attempts',
            'total_questions_answered', 'total_correct_answers',
            'average_score', 'highest_score', 'lowest_score',
            'accuracy_percentage', 'total_time_spent',
            'last_attempt_at', 'updated_at'
        ]