"""
Attempt Service — handles all quiz attempt business logic.

Two main operations:
1. start_attempt()  → user begins a quiz
2. submit_attempt() → user submits answers, get scored

Scoring formula:
    score = (correct_answers / total_questions) * 100
"""

import logging
from django.db import transaction
from django.utils import timezone
from django.db.models import F

from attempts.models import Attempt, AttemptAnswer
from quizzes.models import Quiz, Question
from rest_framework import serializers as drf_serializers

from .analytics_service import update_user_analytics

logger = logging.getLogger(__name__)


def start_attempt(user, quiz_id: int) -> Attempt:
    """
    Starts a new quiz attempt for a user.

    Business rules enforced here:
    - Quiz must exist and be published
    - User cannot have an in_progress attempt for the same quiz
      (they must submit or abandon first)

    Args:
        user: authenticated User instance
        quiz_id: ID of the quiz to attempt

    Returns:
        Attempt instance with status=in_progress
    """
    # Rule 1: Quiz must exist and be published
    try:
        quiz = Quiz.objects.prefetch_related('questions').get(
            id=quiz_id,
            status=Quiz.Status.PUBLISHED
        )
    except Quiz.DoesNotExist:
        raise drf_serializers.ValidationError(
            {'quiz': 'Quiz not found or not available.'}
        )

    # Rule 2: No duplicate in-progress attempts
    existing = Attempt.objects.filter(
        user=user,
        quiz=quiz,
        status=Attempt.Status.IN_PROGRESS
    ).first()

    if existing:
        raise drf_serializers.ValidationError({
            'attempt': f'You already have an in-progress attempt (ID: {existing.id}). Submit or abandon it first.'
        })

    # Create the attempt
    attempt = Attempt.objects.create(
        user=user,
        quiz=quiz,
        status=Attempt.Status.IN_PROGRESS,
        total_questions=quiz.questions.count()
    )

    logger.info(f'Attempt {attempt.id} started by user {user.email} for quiz {quiz_id}')
    return attempt


@transaction.atomic
def submit_attempt(user, attempt_id: int, answers: list) -> Attempt:
    """
    Submits answers for an attempt and calculates the score.

    Args:
        user: authenticated User instance
        attempt_id: ID of the attempt to submit
        answers: list of dicts [{"question_id": 1, "selected_option": "a"}, ...]

    Returns:
        Completed Attempt instance with score populated

    Why @transaction.atomic?
    All answers + score update must succeed together.
    Partial saves would corrupt the score calculation.
    """
    # Validate attempt ownership and status
    try:
        attempt = Attempt.objects.select_related(
            'quiz', 'user'
        ).prefetch_related(
            'quiz__questions'
        ).get(id=attempt_id)
    except Attempt.DoesNotExist:
        raise drf_serializers.ValidationError(
            {'attempt': 'Attempt not found.'}
        )

    if attempt.user != user:
        raise drf_serializers.ValidationError(
            {'attempt': 'This attempt does not belong to you.'}
        )

    if attempt.status != Attempt.Status.IN_PROGRESS:
        raise drf_serializers.ValidationError(
            {'attempt': f'Attempt is already {attempt.status}. Cannot resubmit.'}
        )

    # Build a lookup map for quick question access
    # { question_id: Question instance }
    question_map = {
        q.id: q for q in attempt.quiz.questions.all()
    }

    # Process each submitted answer
    answer_objects = []
    correct_count = 0

    for answer_data in answers:
        question_id = answer_data.get('question_id')
        selected_option = answer_data.get('selected_option', '').lower().strip()

        question = question_map.get(question_id)

        if not question:
            logger.warning(f'Question {question_id} not found in quiz, skipping')
            continue

        is_correct = question.check_answer(selected_option)
        if is_correct:
            correct_count += 1

        answer_objects.append(AttemptAnswer(
            attempt=attempt,
            question=question,
            selected_option=selected_option,
            is_correct=is_correct
        ))

    # Bulk create all answers in one query
    AttemptAnswer.objects.bulk_create(
        answer_objects,
        ignore_conflicts=True  # prevents duplicate answer errors
    )

    # Calculate final score
    total = attempt.total_questions or len(question_map)
    score = round((correct_count / total * 100), 2) if total > 0 else 0.0

    # Update attempt to completed
    attempt.status = Attempt.Status.COMPLETED
    attempt.score = score
    attempt.correct_answers = correct_count
    attempt.total_questions = total
    attempt.completed_at = timezone.now()
    attempt.save(update_fields=[
        'status', 'score', 'correct_answers',
        'total_questions', 'completed_at'
    ])

    logger.info(
        f'Attempt {attempt_id} completed. '
        f'Score: {score}% ({correct_count}/{total})'
    )

    # Update analytics summary (non-blocking — won't fail the submission)
    try:
        update_user_analytics(user, attempt)
    except Exception as e:
        logger.error(f'Analytics update failed for user {user.id}: {str(e)}')

    return attempt


def get_attempt_result(user, attempt_id: int) -> Attempt:
    """
    Returns a completed attempt with full answer details.
    Used to show results page after submission.
    """
    try:
        return Attempt.objects.select_related(
            'quiz', 'user'
        ).prefetch_related(
            'answers__question'
        ).get(
            id=attempt_id,
            user=user
        )
    except Attempt.DoesNotExist:
        raise drf_serializers.ValidationError(
            {'attempt': 'Attempt not found.'}
        )


def get_user_attempts(user):
    """
    Returns all attempts by a user, ordered by most recent.
    Used for quiz history page.
    """
    return (
        Attempt.objects
        .filter(user=user)
        .select_related('quiz')
        .order_by('-started_at')
    )