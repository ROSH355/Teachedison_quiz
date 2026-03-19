from django.contrib import admin
from .models import Attempt, AttemptAnswer


class AttemptAnswerInline(admin.TabularInline):
    model = AttemptAnswer
    extra = 0
    readonly_fields = ['question', 'selected_option', 'is_correct']


@admin.register(Attempt)
class AttemptAdmin(admin.ModelAdmin):
    list_display = ['user', 'quiz', 'status', 'score',
                    'correct_answers', 'total_questions', 'started_at']
    list_filter = ['status']
    inlines = [AttemptAnswerInline]


@admin.register(AttemptAnswer)
class AttemptAnswerAdmin(admin.ModelAdmin):
    list_display = ['attempt', 'question', 'selected_option', 'is_correct']
    list_filter = ['is_correct']