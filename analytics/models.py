"""
UserAnalytics — aggregated performance summary per user.

Why a separate analytics model instead of always querying attempts?
- Querying all attempts every time is expensive at scale
- This acts as a 'materialized summary' — updated after each attempt
- Analytics endpoints become O(1) lookups instead of expensive aggregations

Trade-off: data duplication. Worth it for read-heavy analytics.
"""

from django.db import models
from django.conf import settings


class UserAnalytics(models.Model):
    """
    One record per user — updated after every completed attempt.
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='analytics'
    )

    # Aggregated stats
    total_attempts = models.PositiveIntegerField(default=0)
    completed_attempts = models.PositiveIntegerField(default=0)
    total_questions_answered = models.PositiveIntegerField(default=0)
    total_correct_answers = models.PositiveIntegerField(default=0)

    # Score tracking
    average_score = models.FloatField(default=0.0)
    highest_score = models.FloatField(default=0.0)
    lowest_score = models.FloatField(default=100.0)

    # Engagement
    total_time_spent = models.PositiveIntegerField(
        default=0,
        help_text='Total seconds spent on all attempts'
    )
    last_attempt_at = models.DateTimeField(null=True, blank=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user_analytics'

    def __str__(self):
        return f'Analytics: {self.user.email}'

    @property
    def accuracy_percentage(self):
        """Overall accuracy across all attempts."""
        if self.total_questions_answered == 0:
            return 0.0
        return round(
            (self.total_correct_answers / self.total_questions_answered) * 100,
            2
        )