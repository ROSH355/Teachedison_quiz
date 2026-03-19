from rest_framework.throttling import UserRateThrottle


class QuizCreateThrottle(UserRateThrottle):
    """
    Strict rate limit for quiz creation.
    AI generation is expensive — limit to 10 per hour per user.
    """
    scope = 'quiz_create'