from django.urls import path
from . import views

app_name = 'leaderboard'

urlpatterns = [
    path('<int:quiz_id>/', views.quiz_leaderboard, name='quiz_leaderboard'),
    path('<int:quiz_id>/download/', views.download_csv, name='download_csv'),
    path('<int:quiz_id>/podium/', views.final_podium, name='final_podium'),
]
