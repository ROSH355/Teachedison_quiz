from django.urls import path
from . import views

urlpatterns = [
    path('', views.list_quizzes_view, name='quiz-list'),
    path('create/', views.create_quiz_view, name='quiz-create'),
    path('my-quizzes/', views.my_quizzes_view, name='my-quizzes'),
    path('<int:quiz_id>/', views.quiz_detail_view, name='quiz-detail'),
    path('<int:quiz_id>/publish/', views.publish_quiz_view, name='quiz-publish'),
]