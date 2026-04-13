from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/<int:quiz_id>/', views.login, name='login'),
]
