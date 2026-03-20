from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('send-otp/<int:quiz_id>/', views.send_otp, name='send_otp'),
    path('verify-otp/<int:quiz_id>/', views.verify_otp, name='verify_otp'),
]
