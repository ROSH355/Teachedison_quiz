"""
Attempt views — start and submit quiz attempts.
All routes require authentication.
"""

import logging
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

from .serializers import (
    StartAttemptSerializer,
    SubmitAttemptSerializer,
    AttemptSerializer,
    AttemptResultSerializer
)
from common.services.attempt_service import (
    start_attempt,
    submit_attempt,
    get_attempt_result,
    get_user_attempts
)

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_attempt_view(request):
    """
    POST /api/attempts/start/
    Start a new quiz attempt.

    Body: { "quiz_id": 1 }
    Returns: attempt_id + quiz questions (no correct answers)
    """
    serializer = StartAttemptSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(
            {'error': True, 'details': serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        attempt = start_attempt(
            user=request.user,
            quiz_id=serializer.validated_data['quiz_id']
        )

        # Return attempt ID + questions (correct answers hidden)
        from quizzes.serializers import QuestionSerializer
        questions = QuestionSerializer(
            attempt.quiz.questions.all(),
            many=True
        ).data

        return Response({
            'error': False,
            'message': 'Attempt started. Good luck!',
            'data': {
                'attempt_id': attempt.id,
                'quiz_title': attempt.quiz.title,
                'quiz_topic': attempt.quiz.topic,
                'difficulty': attempt.quiz.difficulty,
                'time_limit': attempt.quiz.time_limit,
                'total_questions': attempt.total_questions,
                'questions': questions
            }
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response(
            {'error': True, 'message': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_attempt_view(request, attempt_id):
    """
    POST /api/attempts/<attempt_id>/submit/
    Submit answers and get scored immediately.

    Body:
    {
        "answers": [
            {"question_id": 1, "selected_option": "a"},
            {"question_id": 2, "selected_option": "c"},
            ...
        ]
    }
    """
    serializer = SubmitAttemptSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(
            {'error': True, 'details': serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        attempt = submit_attempt(
            user=request.user,
            attempt_id=attempt_id,
            answers=serializer.validated_data['answers']
        )

        return Response({
            'error': False,
            'message': 'Attempt submitted successfully!',
            'data': AttemptResultSerializer(attempt).data
        })

    except Exception as e:
        return Response(
            {'error': True, 'message': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def attempt_result_view(request, attempt_id):
    """
    GET /api/attempts/<attempt_id>/result/
    Retrieve full results of a completed attempt.
    """
    try:
        attempt = get_attempt_result(request.user, attempt_id)
        return Response({
            'error': False,
            'data': AttemptResultSerializer(attempt).data
        })
    except Exception as e:
        return Response(
            {'error': True, 'message': str(e)},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def attempt_history_view(request):
    """
    GET /api/attempts/history/
    Returns paginated list of all user's past attempts.
    """
    attempts = get_user_attempts(request.user)

    paginator = PageNumberPagination()
    paginator.page_size = 10
    page = paginator.paginate_queryset(attempts, request)

    serializer = AttemptSerializer(page, many=True)
    return paginator.get_paginated_response({
        'error': False,
        'data': serializer.data
    })