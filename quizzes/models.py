"""
Quiz and Question models.

Quiz → created by a User (admin/teacher)
Question → belongs to a Quiz, holds 4 MCQ options

Design choice: We store options as option_a, option_b, option_c, option_d
instead of a separate Option table because:
- These quizzes are always MCQ with exactly 4 options
- Fewer JOINs = faster queries
- Simpler serialization
"""

from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


class Quiz(models.Model):

    class Difficulty(models.TextChoices):
        EASY = 'easy', 'Easy'
        MEDIUM = 'medium', 'Medium'
        HARD = 'hard', 'Hard'

    class Status(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        PUBLISHED = 'published', 'Published'
        ARCHIVED = 'archived', 'Archived'

    # Who created this quiz
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_quizzes'
    )

    # Core fields
    title = models.CharField(max_length=255)
    topic = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    difficulty = models.CharField(
        max_length=10,
        choices=Difficulty.choices,
        default=Difficulty.MEDIUM
    )

    # How many questions to generate via AI
    question_count = models.PositiveIntegerField(
        default=5,
        validators=[MinValueValidator(1), MaxValueValidator(20)]
    )

    # Lifecycle
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.DRAFT
    )

    # Time limit in minutes (optional)
    time_limit = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text='Time limit in minutes. Null means no limit.'
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'quizzes'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.title} ({self.difficulty})'

    @property
    def is_published(self):
        return self.status == self.Status.PUBLISHED

    @property
    def total_questions(self):
        return self.questions.count()


class Question(models.Model):
    """
    A single MCQ question belonging to a Quiz.

    correct_answer stores which option letter is correct: 'a', 'b', 'c', or 'd'
    This makes scoring dead simple:
        user_answer == question.correct_answer → correct
    """

    class CorrectAnswer(models.TextChoices):
        A = 'a', 'Option A'
        B = 'b', 'Option B'
        C = 'c', 'Option C'
        D = 'd', 'Option D'

    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name='questions'
    )

    # Question content
    question_text = models.TextField()

    # Four options
    option_a = models.CharField(max_length=500)
    option_b = models.CharField(max_length=500)
    option_c = models.CharField(max_length=500)
    option_d = models.CharField(max_length=500)

    # Which option is correct
    correct_answer = models.CharField(
        max_length=1,
        choices=CorrectAnswer.choices
    )

    # Optional explanation shown after attempt
    explanation = models.TextField(blank=True, null=True)

    # Order within the quiz
    order = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'questions'
        ordering = ['order', 'created_at']

    def __str__(self):
        return f'Q{self.order}: {self.question_text[:60]}...'

    def check_answer(self, answer: str) -> bool:
        """
        Simple helper used during attempt submission.
        Centralizes answer checking logic in one place.
        """
        return answer.lower() == self.correct_answer.lower()