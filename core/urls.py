from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('landing/', views.landing, name='landing'),
    path('select-role/', views.select_role, name='select_role'),
    path('landing/api/quiz-states/', views.quiz_state_api, name='quiz_state_api'),
]
