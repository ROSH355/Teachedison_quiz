from django.db import models
from django.conf import settings
from quizzes.models import Quiz, Question


class Attempt(models.Model):

    class Status(models.TextChoices):
        IN_PROGRESS = "in_progress", "In Progress"
        COMPLETED = "completed", "Completed"
        ABANDONED = "abandoned", "Abandoned"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="attempts"
    )
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="attempts")

    # Lifecycle tracking
    status = models.CharField(
        max_length=15, choices=Status.choices, default=Status.IN_PROGRESS
    )

    # Score fields — populated when attempt is submitted
    score = models.FloatField(null=True, blank=True)  # percentage 0-100
    total_questions = models.PositiveIntegerField(default=0)
    correct_answers = models.PositiveIntegerField(default=0)

    # Timing
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "attempts"
        ordering = ["-started_at"]

    def __str__(self):
        return f"{self.user.email} → {self.quiz.title} ({self.status})"

    @property
    def duration_seconds(self):
        """How long the attempt took in seconds."""
        if self.completed_at and self.started_at:
            return (self.completed_at - self.started_at).seconds
        return None

    @property
    def passed(self):
        """Simple pass/fail — score >= 60% is a pass."""
        if self.score is None:
            return None
        return self.score >= 60.0


class AttemptAnswer(models.Model):

    attempt = models.ForeignKey(
        Attempt, on_delete=models.CASCADE, related_name="answers"
    )
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name="attempt_answers"
    )

    selected_option = models.CharField(
        max_length=1,
        choices=[("a", "A"), ("b", "B"), ("c", "C"), ("d", "D")],
        null=True,
        blank=True,  # null means unanswered/skipped
    )

    is_correct = models.BooleanField(default=False)
    answered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "attempt_answers"
        # One answer per question per attempt — enforce uniqueness
        unique_together = ["attempt", "question"]

    def __str__(self):
        status = "✓" if self.is_correct else "✗"
        return f"{status} Attempt#{self.attempt_id} Q#{self.question_id}"
