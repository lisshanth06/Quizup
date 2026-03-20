from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.views.decorators.http import require_http_methods
from django.db import transaction
from .models import OTP
from quizzes.models import Quiz, Participant, AllowedParticipant
import re
import logging
from urllib.parse import urlencode

logger = logging.getLogger(__name__)


def validate_college_email(email):
    """
    Example: 2024it0054@svce.ac.in
    """
    pattern = r'^\d{4}[a-z]{2}\d{4}@svce\.ac\.in$'
    return bool(re.fullmatch(pattern, email.lower()))


@require_http_methods(["GET", "POST"])
def send_otp(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id, status=Quiz.Status.LIVE)

    if request.method == "POST":
        email = request.POST.get("email", "").strip().lower()
        name = request.POST.get("name", "").strip()

        if not email or not name:
            messages.error(request, "Name and email are required.")
            return render(request, "accounts/send_otp.html", {"quiz": quiz})

        # Check if email is in the allowed list
        if not AllowedParticipant.objects.filter(quiz=quiz, email=email).exists():
            return render(request, "accounts/not_allowed.html", {"quiz": quiz, "email": email})

        # Wait, the prompt says: "Only users whose email is uploaded by admin can attend the quiz. Others must be blocked"
        # We don't enforce college email if admin uploaded it, but let's keep it if we want, or remove it?
        # The prompt says "Only users whose email is uploaded by admin can attend the quiz". The previous college email validation might be redundant, but let's keep it just in case, or rather not, if admin uploads arbitrary emails. Actually, let's keep validate_college_email but prioritize the AllowedParticipant check. Wait, I will remove validate_college_email because AllowedParticipant is the only source of truth now.


        # Prevent OTP spam
        recent_otp = OTP.objects.filter(
            email=email,
            quiz=quiz,
            created_at__gte=timezone.now()
            - timezone.timedelta(
                seconds=settings.OTP_RESEND_COOLDOWN_SECONDS
            ),
            is_used=False,
        ).first()

        if recent_otp and recent_otp.is_valid():
            messages.error(
                request,
                f"Wait {settings.OTP_RESEND_COOLDOWN_SECONDS}s before retrying.",
            )
            return render(request, "accounts/send_otp.html", {"quiz": quiz})

        otp_code = OTP.generate_otp()
        otp = OTP.objects.create(
            email=email,
            otp_code=otp_code,
            quiz=quiz,
        )

        try:
            send_mail(
                subject=f"OTP for {quiz.name}",
                message=(
                    f"Your OTP is: {otp_code}\n\n"
                    f"Valid for {settings.OTP_EXPIRY_MINUTES} minutes."
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )

            # Do not use session for sending OTP to avoid multiple tabs issue.
            # Pass data in URL query params.
            query_string = urlencode({'email': email, 'name': name})
            messages.success(request, "OTP sent successfully.")
            return redirect(f"{redirect('accounts:verify_otp', quiz_id=quiz.id).url}?{query_string}")

        except Exception as e:
            logger.error(f"Failed to send OTP email to {email}: {str(e)}", exc_info=True)
            otp.delete()
            if settings.DEBUG:
                messages.error(request, f"Failed to send OTP email. Error: {str(e)}")
            else:
                messages.error(request, "Failed to send OTP email. Please try again later.")

    return render(request, "accounts/send_otp.html", {"quiz": quiz})


@require_http_methods(["GET", "POST"])
def verify_otp(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id, status=Quiz.Status.LIVE)

    # Use query params instead of session
    pending_email = request.GET.get("email") or request.POST.get("email")
    pending_name = request.GET.get("name") or request.POST.get("name")

    if not pending_email or not pending_name:
        messages.error(request, "Session expired or invalid link. Start again.")
        return redirect("accounts:send_otp", quiz_id=quiz.id)

    if request.method == "POST":
        otp_code = request.POST.get("otp", "").strip()

        if not otp_code:
            messages.error(request, "Enter the OTP.")
            return render(
                request,
                "accounts/verify_otp.html",
                {"quiz": quiz, "email": pending_email, "name": pending_name},
            )

        otp = OTP.objects.filter(
            email=pending_email,
            quiz=quiz,
            otp_code=otp_code,
            is_used=False,
        ).order_by("-created_at").first()

        if not otp or not otp.is_valid():
            messages.error(request, "Invalid or expired OTP.")
            return render(
                request,
                "accounts/verify_otp.html",
                {"quiz": quiz, "email": pending_email, "name": pending_name},
            )

        with transaction.atomic():
            otp.is_used = True
            otp.save()

            participant, _ = Participant.objects.get_or_create(
                quiz=quiz,
                email=pending_email,
                defaults={
                    "name": pending_name,
                    "verified": True,
                },
            )

        # Rotate session (security)
        request.session.flush()
        request.session["participant_id"] = participant.id
        request.session["quiz_id"] = quiz.id

        messages.success(request, "Verification successful!")
        return redirect("quizzes:quiz_rules", quiz_id=quiz.id)

    return render(
        request,
        "accounts/verify_otp.html",
        {"quiz": quiz, "email": pending_email, "name": pending_name},
    )
