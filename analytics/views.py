from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .serializers import UserAnalyticsSerializer
from common.services.analytics_service import get_user_analytics
from common.services.attempt_service import get_user_attempts
from attempts.serializers import AttemptSerializer


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def performance_view(request):
    """
    GET /api/analytics/performance/
    Returns the current user's aggregated performance stats.
    """
    analytics = get_user_analytics(request.user)
    return Response({
        'error': False,
        'data': UserAnalyticsSerializer(analytics).data
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def history_view(request):
    """
    GET /api/analytics/history/
    Returns recent attempts with scores — the user's quiz history.
    """
    attempts = get_user_attempts(request.user)[:20]
    return Response({
        'error': False,
        'data': AttemptSerializer(attempts, many=True).data
    })