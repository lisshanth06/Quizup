from django.urls import path

from . import views

app_name = "dashboard"

urlpatterns = [
    path("login/", views.login, name="login"),
    path("logout/", views.logout, name="logout"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("", views.dashboard, name="admin_index"),
    path("quiz/create/", views.quiz_create, name="quiz_create"),
    path("quiz/<int:quiz_id>/", views.quiz_manage, name="quiz_manage"),
    path("quiz/<int:quiz_id>/edit/", views.quiz_edit, name="quiz_edit"),
    path("quiz/<int:quiz_id>/deploy/", views.quiz_deploy, name="quiz_deploy"),
    path("quiz/<int:quiz_id>/start/", views.quiz_start, name="quiz_start"),
    path("quiz/<int:quiz_id>/end/", views.quiz_end, name="quiz_end"),
    path("quiz/<int:quiz_id>/delete/", views.quiz_delete, name="quiz_delete"),
    path("quiz/<int:quiz_id>/toggle-leaderboard/", views.toggle_leaderboard, name="toggle_leaderboard"),
    path("quiz/<int:quiz_id>/upload-emails/", views.upload_emails, name="upload_emails"),
    path("quiz/<int:quiz_id>/clear-emails/", views.clear_emails, name="clear_emails"),
    path(
        "quiz/<int:quiz_id>/question/create/",
        views.question_create,
        name="question_create",
    ),
    path("question/<int:question_id>/delete/", views.question_delete, name="question_delete"),
    path(
        "quiz/<int:quiz_id>/leaderboard/",
        views.quiz_leaderboard_view,
        name="quiz_leaderboard",
    ),
    path("quiz/<int:quiz_id>/live/", views.quiz_live_leaderboard, name="quiz_live_leaderboard"),
    path("quiz/<int:quiz_id>/live-data/", views.quiz_live_data, name="quiz_live_data"),
    path("quiz/<int:quiz_id>/questions/upload-csv/", views.question_upload_csv, name="question_upload_csv"),
    path("quiz/<int:quiz_id>/download-emails/", views.download_allowed_emails, name="download_emails"),
    path("quiz/<int:quiz_id>/add-email/", views.manual_add_email, name="add_email"),
    path("quiz/<int:quiz_id>/check-email/", views.check_email_presence, name="check_email"),
    path("quiz/<int:quiz_id>/delete-participant/", views.delete_participant, name="delete_participant"),
    path("quiz/<int:quiz_id>/participants/", views.participants_list, name="participants_list"),
]
