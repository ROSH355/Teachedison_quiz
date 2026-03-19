from rest_framework import serializers
from .models import Attempt, AttemptAnswer
from quizzes.serializers import QuestionWithAnswerSerializer


class StartAttemptSerializer(serializers.Serializer):
    """Just needs quiz_id to start an attempt."""

    quiz_id = serializers.IntegerField()


class AnswerInputSerializer(serializers.Serializer):
    """Single answer input — question + selected option."""

    question_id = serializers.IntegerField()
    selected_option = serializers.ChoiceField(choices=["a", "b", "c", "d"])


class SubmitAttemptSerializer(serializers.Serializer):
    """
    Validates the full submission payload.
    answers is a list of AnswerInputSerializer objects.
    """

    answers = AnswerInputSerializer(many=True)

    def validate_answers(self, value):
        if not value:
            raise serializers.ValidationError("You must submit at least one answer.")
        return value


class AttemptAnswerResultSerializer(serializers.ModelSerializer):
    """Shows each answer with the correct answer revealed."""

    question = QuestionWithAnswerSerializer(read_only=True)

    class Meta:
        model = AttemptAnswer
        fields = ["question", "selected_option", "is_correct"]


class AttemptSerializer(serializers.ModelSerializer):
    """Lightweight attempt info for list views."""

    quiz_title = serializers.CharField(source="quiz.title", read_only=True)
    quiz_topic = serializers.CharField(source="quiz.topic", read_only=True)
    passed = serializers.ReadOnlyField()
    duration_seconds = serializers.ReadOnlyField()

    class Meta:
        model = Attempt
        fields = [
            "id",
            "quiz_title",
            "quiz_topic",
            "status",
            "score",
            "correct_answers",
            "total_questions",
            "passed",
            "duration_seconds",
            "started_at",
            "completed_at",
        ]


class AttemptResultSerializer(serializers.ModelSerializer):
    """
    Full attempt result — used after submission.
    Includes every question with correct answers revealed.
    """

    quiz_title = serializers.CharField(source="quiz.title", read_only=True)
    quiz_topic = serializers.CharField(source="quiz.topic", read_only=True)
    answers = AttemptAnswerResultSerializer(many=True, read_only=True)
    passed = serializers.ReadOnlyField()
    duration_seconds = serializers.ReadOnlyField()

    class Meta:
        model = Attempt
        fields = [
            "id",
            "quiz_title",
            "quiz_topic",
            "status",
            "score",
            "correct_answers",
            "total_questions",
            "passed",
            "duration_seconds",
            "started_at",
            "completed_at",
            "answers",
        ]
