from django.contrib import admin
from .models import Quiz, Question


class QuestionInline(admin.TabularInline):
    """Show questions directly inside the Quiz admin page."""
    model = Question
    extra = 0
    fields = ['question_text', 'option_a', 'option_b',
              'option_c', 'option_d', 'correct_answer', 'order']


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ['title', 'topic', 'difficulty', 'status',
                    'question_count', 'created_by', 'created_at']
    list_filter = ['difficulty', 'status']
    search_fields = ['title', 'topic']
    inlines = [QuestionInline]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['question_text', 'quiz', 'correct_answer', 'order']
    list_filter = ['correct_answer']
    search_fields = ['question_text']