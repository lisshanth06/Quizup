from django.urls import path
from . import views

app_name = 'quizzes'

urlpatterns = [
    path('<int:quiz_id>/', views.quiz_detail, name='quiz_detail'),

    path(
        '<int:quiz_id>/submit/',
        views.submit_answer,
        name='submit_answer'
    ),

    path('<int:quiz_id>/rules/', views.quiz_rules, name='quiz_rules'),

    path('<int:quiz_id>/waiting/', views.quiz_waiting, name='quiz_waiting'),

    path(
        '<int:quiz_id>/completed/',
        views.quiz_submitted,
        name='quiz_submitted'
    ),

    path(
        '<int:quiz_id>/report-cheat/',
        views.report_cheat,
        name='report_cheat'
    ),
]
