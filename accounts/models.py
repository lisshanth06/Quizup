from django.db import models
from django.utils import timezone
from django.core.validators import EmailValidator
import secrets
from datetime import timedelta
from django.conf import settings


class OTP(models.Model):
    """OTP model for email verification"""
    email = models.EmailField(max_length=255, db_index=True)
    otp_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)
    quiz = models.ForeignKey('quizzes.Quiz', on_delete=models.CASCADE, null=True, blank=True)
    
    class Meta:
        db_table = 'otp'
        indexes = [
            models.Index(fields=['email', 'is_used']),
            models.Index(fields=['created_at']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"OTP for {self.email}"
    
    def is_expired(self):
        """Check if OTP has expired"""
        expiry_time = self.created_at + timedelta(minutes=settings.OTP_EXPIRY_MINUTES)
        return timezone.now() > expiry_time
    
    def is_valid(self):
        """Check if OTP is valid and not expired"""
        return not self.is_used and not self.is_expired()
    
    @staticmethod
    def generate_otp():
        """Generate a 6-digit OTP"""
        return ''.join([str(secrets.randbelow(10)) for _ in range(6)])
