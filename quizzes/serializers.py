"""
Quiz serializers handle input validation and output formatting.

Two serializers:
- QuizCreateSerializer: validates quiz creation input
- QuizSerializer: formats quiz data for responses (with questions)
"""

from rest_framework import serializers
from .models import Quiz, Question


class QuestionSerializer(serializers.ModelSerializer):
    """
    Used for READ operations — showing questions to users.
    Note: correct_answer is excluded here intentionally.
    We only reveal it in the attempt results, not upfront.
    """
    class Meta:
        model = Question
        fields = [
            'id', 'question_text',
            'option_a', 'option_b', 'option_c', 'option_d',
            'order'
        ]
        # correct_answer deliberately excluded from public view


class QuestionWithAnswerSerializer(serializers.ModelSerializer):
    """
    Used ONLY in admin views or after attempt completion.
    Reveals correct_answer and explanation.
    """
    class Meta:
        model = Question
        fields = [
            'id', 'question_text',
            'option_a', 'option_b', 'option_c', 'option_d',
            'correct_answer', 'explanation', 'order'
        ]


class QuizCreateSerializer(serializers.ModelSerializer):
    """
    Validates quiz creation input.
    Only accepts the fields a user should provide.
    created_by, status are set automatically in the service.
    """
    class Meta:
        model = Quiz
        fields = [
            'title', 'topic', 'description',
            'difficulty', 'question_count', 'time_limit'
        ]

    def validate_question_count(self, value):
        if value < 1 or value > 20:
            raise serializers.ValidationError(
                'Question count must be between 1 and 20.'
            )
        return value

    def validate_topic(self, value):
        if len(value.strip()) < 3:
            raise serializers.ValidationError(
                'Topic must be at least 3 characters.'
            )
        return value.strip()


class QuizSerializer(serializers.ModelSerializer):
    """
    Full quiz representation for list and detail responses.
    Includes nested questions and creator info.
    """
    questions = QuestionSerializer(many=True, read_only=True)
    created_by_name = serializers.CharField(
        source='created_by.full_name',
        read_only=True
    )
    total_questions = serializers.ReadOnlyField()
    is_published = serializers.ReadOnlyField()

    class Meta:
        model = Quiz
        fields = [
            'id', 'title', 'topic', 'description',
            'difficulty', 'question_count', 'time_limit',
            'status', 'is_published', 'total_questions',
            'created_by_name', 'questions', 'created_at'
        ]


class QuizListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for list views.
    Excludes questions to keep list responses fast and small.
    """
    created_by_name = serializers.CharField(
        source='created_by.full_name',
        read_only=True
    )
    total_questions = serializers.ReadOnlyField()

    class Meta:
        model = Quiz
        fields = [
            'id', 'title', 'topic', 'difficulty',
            'question_count', 'total_questions', 'time_limit',
            'status', 'created_by_name', 'created_at'
        ]