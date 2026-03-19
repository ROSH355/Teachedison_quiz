"""
Analytics Service — updates aggregated user stats after each attempt.

Called automatically after every successful attempt submission.
Updates UserAnalytics in-place so dashboard queries stay fast.
"""

import logging
from django.db import transaction
from analytics.models import UserAnalytics
from django.utils import timezone

logger = logging.getLogger(__name__)


@transaction.atomic
def update_user_analytics(user, attempt) -> UserAnalytics:
    """
    Updates or creates the UserAnalytics record after an attempt.

    Uses get_or_create so first-time users get an analytics record
    automatically — no manual setup needed.

    Args:
        user: User instance
        attempt: completed Attempt instance
    """
    analytics, created = UserAnalytics.objects.get_or_create(user=user)

    if created:
        logger.info(f'Created new analytics record for user {user.email}')

    # Update counters
    analytics.total_attempts += 1
    analytics.completed_attempts += 1
    analytics.total_questions_answered += attempt.total_questions
    analytics.total_correct_answers += attempt.correct_answers

    # Update score tracking
    score = attempt.score or 0.0

    # Recalculate average score
    # Formula: new_avg = ((old_avg * (n-1)) + new_score) / n
    n = analytics.completed_attempts
    analytics.average_score = round(
        ((analytics.average_score * (n - 1)) + score) / n,
        2
    )

    # Track highest and lowest scores
    if score > analytics.highest_score:
        analytics.highest_score = score

    if analytics.lowest_score == 100.0 or score < analytics.lowest_score:
        analytics.lowest_score = score

    # Track total time spent
    if attempt.duration_seconds:
        analytics.total_time_spent += attempt.duration_seconds

    analytics.last_attempt_at = timezone.now()
    analytics.save()

    return analytics


def get_user_analytics(user) -> UserAnalytics:
    """
    Returns analytics for a user, creating default record if needed.
    """
    analytics, _ = UserAnalytics.objects.get_or_create(user=user)
    return analytics