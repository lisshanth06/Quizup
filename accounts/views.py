from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from quizzes.models import Quiz, Participant, AllowedParticipant
import logging

logger = logging.getLogger(__name__)

@require_http_methods(["GET", "POST"])
def login(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id, status=Quiz.Status.LIVE)

    if request.method == "POST":
        email = request.POST.get("email", "").strip().lower()
        name = request.POST.get("name", "").strip()

        if not email or not name:
            messages.error(request, "Name and email are required.")
            return render(request, "accounts/login.html", {"quiz": quiz})

        # Check if email is in the allowed list
        if not AllowedParticipant.objects.filter(quiz=quiz, email=email).exists():
            return render(request, "accounts/not_allowed.html", {"quiz": quiz, "email": email})

        # Login directly since email exists
        participant, _ = Participant.objects.get_or_create(
            quiz=quiz,
            email=email,
            defaults={
                "name": name,
                "verified": True,
            },
        )
        
        # If the participant already exists but the verified flag is false, correct it.
        # This resolves the issue where "users are getting incorrect states".
        if not participant.verified:
            participant.verified = True
            participant.save(update_fields=["verified"])

        # Create session
        request.session.flush()
        request.session["participant_id"] = participant.id
        request.session["quiz_id"] = quiz.id

        messages.success(request, "Login successful!")
        return redirect("quizzes:quiz_rules", quiz_id=quiz.id)

    return render(request, "accounts/login.html", {"quiz": quiz})
