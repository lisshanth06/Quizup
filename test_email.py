import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'quiz_app_csi.settings')
django.setup()

from django.core.mail import send_mail
from django.conf import settings

print("=" * 50)
print("Testing Email Configuration")
print("=" * 50)
print(f"EMAIL_HOST: {settings.EMAIL_HOST}")
print(f"EMAIL_PORT: {settings.EMAIL_PORT}")
print(f"EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
print(f"EMAIL_USE_SSL: {settings.EMAIL_USE_SSL}")
print(f"EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
print(f"DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
print("=" * 50)

try:
    send_mail(
        'Test Email from Quiz App',
        'This is a test email to verify SMTP configuration.',
        settings.DEFAULT_FROM_EMAIL,
        [settings.EMAIL_HOST_USER],  # Send to yourself
        fail_silently=False,
    )
    print("✓ Email sent successfully!")
    print("Check your inbox:", settings.EMAIL_HOST_USER)
except Exception as e:
    print(f"✗ Error sending email: {e}")
    import traceback
    traceback.print_exc()