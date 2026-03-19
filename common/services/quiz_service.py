"""
Quiz Service — business logic for quiz creation and retrieval.

Views call this. This calls ai_service and the ORM.
No HTTP logic here, no serializer logic here — just domain logic.
"""

import logging
from django.db import transaction
from quizzes.models import Quiz, Question
from .ai_service import generate_quiz_questions

logger = logging.getLogger(__name__)


@transaction.atomic
def create_quiz_with_questions(user, validated_data: dict) -> Quiz:
    """
    Creates a Quiz and generates Questions via AI in one transaction.

    Why @transaction.atomic?
    If the question creation fails halfway through,
    the entire quiz is rolled back. No orphaned quizzes with 0 questions.

    Args:
        user: the authenticated user creating the quiz
        validated_data: cleaned data from QuizSerializer

    Returns:
        Quiz instance with all questions created
    """
    # Extract question count before creating quiz
    question_count = validated_data.get('question_count', 5)
    topic = validated_data.get('topic')
    difficulty = validated_data.get('difficulty', 'medium')

    # Step 1: Create the Quiz record
    quiz = Quiz.objects.create(
        created_by=user,
        **validated_data
    )
    logger.info(f'Quiz created: {quiz.id} - {quiz.title}')

    # Step 2: Generate questions via AI
    logger.info(f'Generating {question_count} questions for topic: {topic}')
    ai_questions = generate_quiz_questions(topic, difficulty, question_count)

    # Step 3: Bulk create questions for performance
    # Why bulk_create? One DB query instead of N queries
    question_objects = [
        Question(
            quiz=quiz,
            question_text=q['question_text'],
            option_a=q['option_a'],
            option_b=q['option_b'],
            option_c=q['option_c'],
            option_d=q['option_d'],
            correct_answer=q['correct_answer'],
            explanation=q.get('explanation', ''),
            order=index
        )
        for index, q in enumerate(ai_questions)
    ]

    Question.objects.bulk_create(question_objects)
    logger.info(f'Created {len(question_objects)} questions for quiz {quiz.id}')

    # Refresh to get the questions relation populated
    quiz.refresh_from_db()
    return quiz


def get_published_quizzes():
    """
    Returns all published quizzes with optimized queries.

    select_related('created_by') fetches the user in the SAME query
    instead of a separate query per quiz (N+1 problem prevention).
    prefetch_related('questions') fetches all questions in one extra query.
    """
    return (
        Quiz.objects
        .filter(status=Quiz.Status.PUBLISHED)
        .select_related('created_by')
        .prefetch_related('questions')
        .order_by('-created_at')
    )


def get_quiz_detail(quiz_id: int) -> Quiz:
    """
    Returns a single quiz with all questions.
    Raises Quiz.DoesNotExist if not found — view handles the 404.
    """
    return (
        Quiz.objects
        .select_related('created_by')
        .prefetch_related('questions')
        .get(id=quiz_id, status=Quiz.Status.PUBLISHED)
    )


def get_user_quizzes(user):
    """Returns all quizzes created by a specific user (admin view)."""
    return (
        Quiz.objects
        .filter(created_by=user)
        .prefetch_related('questions')
        .order_by('-created_at')
    )


def publish_quiz(quiz_id: int, user) -> Quiz:
    """
    Publishes a draft quiz. Only the creator or admin can publish.
    """
    quiz = Quiz.objects.get(id=quiz_id)

    if quiz.created_by != user and not user.is_admin:
        raise PermissionError('You do not have permission to publish this quiz.')

    if quiz.questions.count() == 0:
        raise ValueError('Cannot publish a quiz with no questions.')

    quiz.status = Quiz.Status.PUBLISHED
    quiz.save(update_fields=['status', 'updated_at'])
    return quiz