import csv
from io import TextIOWrapper

from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods
from django.views.decorators.cache import never_cache


from quizzes.models import Quiz, Question, AllowedParticipant
from leaderboard.views import calculate_quiz_scores


# ------------------------------------------------------------------
# ADMIN AUTH DECORATOR (NO Django Admin UI)
# ------------------------------------------------------------------

def admin_login_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.session.get("is_admin"):
            return redirect("dashboard:login")
        return view_func(request, *args, **kwargs)

    return never_cache(wrapper)


# ------------------------------------------------------------------
# AUTH
# ------------------------------------------------------------------

@require_http_methods(["GET", "POST"])
def login(request):
    if request.method == "GET":
        request.session.pop("is_admin", None)

    if request.method == "POST":
        ADMIN_PASSWORD = "XLevi@00"
        if request.POST.get("password") == ADMIN_PASSWORD:
            request.session["is_admin"] = True
            messages.success(request, "Logged in successfully.")
            return redirect("dashboard:dashboard")
        messages.error(request, "Invalid password.")

    return render(request, "dashboard/login.html")


@require_http_methods(["POST"])
def logout(request):
    request.session.flush()
    return redirect("dashboard:login")


# ------------------------------------------------------------------
# DASHBOARD HOME
# ------------------------------------------------------------------

@admin_login_required
def dashboard(request):
    quizzes = Quiz.objects.all().order_by("-created_at")
    for quiz in quizzes:
        quiz.active_participants_count = quiz.participants.filter(
            verified=True, has_completed=False
        ).count()
    return render(request, "dashboard/dashboard.html", {"quizzes": quizzes})


# ------------------------------------------------------------------
# QUIZ MANAGEMENT
# ------------------------------------------------------------------

@admin_login_required
def quiz_manage(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    questions = quiz.questions.all().order_by("order")
    allowed_participants = quiz.allowed_participants.all()
    return render(
        request,
        "dashboard/quiz_manage.html",
        {"quiz": quiz, "questions": questions, "allowed_participants": allowed_participants},
    )


@admin_login_required
@require_http_methods(["POST"])
def quiz_create(request):
    name = request.POST.get("name", "").strip()
    if not name:
        messages.error(request, "Quiz name required.")
        return redirect("dashboard:dashboard")

    quiz = Quiz.objects.create(name=name)
    messages.success(request, "Quiz created.")
    return redirect("dashboard:quiz_manage", quiz_id=quiz.id)


@admin_login_required
@require_http_methods(["POST"])
def quiz_edit(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)

    if quiz.status != Quiz.Status.DRAFT:
        messages.error(request, "Cannot edit deployed quiz.")
        return redirect("dashboard:quiz_manage", quiz_id=quiz_id)

    quiz.name = request.POST.get("name", quiz.name)
    quiz.save(update_fields=["name", "updated_at"])
    messages.success(request, "Quiz updated.")
    return redirect("dashboard:quiz_manage", quiz_id=quiz_id)


@admin_login_required
@require_http_methods(["POST"])
def quiz_deploy(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)

    if quiz.status != Quiz.Status.DRAFT:
        messages.error(request, "Quiz already deployed.")
        return redirect("dashboard:quiz_manage", quiz_id=quiz_id)

    quiz.deploy()
    messages.success(request, "Quiz is LIVE.")
    return redirect("dashboard:quiz_manage", quiz_id=quiz_id)


@admin_login_required
@require_http_methods(["POST"])
def quiz_end(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)

    if quiz.status != Quiz.Status.LIVE:
        messages.error(request, "Quiz not live.")
        return redirect("dashboard:quiz_manage", quiz_id=quiz_id)

    quiz.end()
    messages.success(request, "Quiz ended.")
    return redirect("dashboard:quiz_manage", quiz_id=quiz_id)


@admin_login_required
@require_http_methods(["POST"])
def quiz_start(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    if quiz.status != Quiz.Status.LIVE:
        messages.error(request, "Cannot start a quiz that isn't LIVE.")
        return redirect("dashboard:quiz_manage", quiz_id=quiz_id)
        
    quiz.is_active = True
    quiz.save(update_fields=["is_active"])
    messages.success(request, "Quiz is now ACTIVE! Users are transitioning.")
    return redirect("dashboard:quiz_manage", quiz_id=quiz_id)


@admin_login_required
@require_http_methods(["POST"])
def quiz_delete(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)

    if quiz.status == Quiz.Status.LIVE:
        messages.error(request, "Cannot delete a LIVE quiz.")
        return redirect("dashboard:dashboard")

    quiz.delete()
    messages.success(request, "Quiz deleted.")
    return redirect("dashboard:dashboard")


@admin_login_required
@require_http_methods(["POST"])
def toggle_leaderboard(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    quiz.show_leaderboard = not quiz.show_leaderboard
    quiz.save(update_fields=["show_leaderboard"])
    msg = "published" if quiz.show_leaderboard else "hidden"
    return JsonResponse({"success": True, "message": f"Leaderboard {msg}."})


# ------------------------------------------------------------------
# ALLOWED PARTICIPANTS (CSV UPLOAD)
# ------------------------------------------------------------------

@admin_login_required
@require_http_methods(["POST"])
def upload_emails(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    
    if quiz.status != Quiz.Status.DRAFT:
        return JsonResponse({"success": False, "message": "Cannot modify allowed participants after deployment."})

    if "csv_file" not in request.FILES:
        return JsonResponse({"success": False, "message": "No file uploaded."})

    csv_file = request.FILES["csv_file"]
    if not csv_file.name.endswith(".csv"):
        return JsonResponse({"success": False, "message": "File must be a CSV."})

    try:
        decoded_file = csv_file.read().decode("utf-8").splitlines()
        reader = csv.reader(decoded_file)
        
        email_list = []
        for row in reader:
            for item in row:
                email = item.strip().lower()
                if "@" in email:  # Basic email check
                    email_list.append(email)
        
        # Insert avoiding duplicates
        existing_emails = set(AllowedParticipant.objects.filter(quiz=quiz).values_list("email", flat=True))
        new_emails = set(email_list) - existing_emails
        
        AllowedParticipant.objects.bulk_create([
            AllowedParticipant(quiz=quiz, email=e) for e in new_emails
        ])

        return JsonResponse({"success": True, "message": f"Successfully added {len(new_emails)} new emails."})
    except Exception as e:
        return JsonResponse({"success": False, "message": f"Error processing file: {e}"})


@admin_login_required
@require_http_methods(["POST"])
def clear_emails(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    
    if quiz.status != Quiz.Status.DRAFT:
        messages.error(request, "Cannot clear allowed participants after deployment.")
        return redirect("dashboard:quiz_manage", quiz_id=quiz_id)

    deleted_count, _ = AllowedParticipant.objects.filter(quiz=quiz).delete()
    messages.success(request, f"Cleared {deleted_count} allowed emails.")
    return redirect("dashboard:quiz_manage", quiz_id=quiz_id)


@admin_login_required
@require_http_methods(["POST"])
def manual_add_email(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)

    if quiz.status != Quiz.Status.DRAFT:
        return JsonResponse({"success": False, "message": "Cannot modify participants after deployment."})

    email = request.POST.get("email", "").strip().lower()
    if not email or "@" not in email:
        return JsonResponse({"success": False, "message": "Invalid email address."})

    if AllowedParticipant.objects.filter(quiz=quiz, email=email).exists():
        return JsonResponse({"success": False, "message": "Email already in list."})

    AllowedParticipant.objects.create(quiz=quiz, email=email)
    return JsonResponse({"success": True, "message": f"Added {email}."})


@admin_login_required
@require_http_methods(["GET"])
def check_email_presence(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    email = request.GET.get("email", "").strip().lower()

    if not email:
        return JsonResponse({"exists": False, "message": "Email required."})

    exists = AllowedParticipant.objects.filter(quiz=quiz, email=email).exists()
    return JsonResponse({"exists": exists, "message": "Participant found." if exists else "Participant not found."})


@admin_login_required
@require_http_methods(["POST"])
def delete_participant(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    email = request.POST.get("email", "").strip().lower()

    if quiz.status != Quiz.Status.DRAFT:
        return JsonResponse({"success": False, "message": "Cannot delete participants after deployment."})

    try:
        participant = AllowedParticipant.objects.get(quiz=quiz, email=email)
        participant.delete()
        return JsonResponse({"success": True, "message": f"Removed {email}."})
    except AllowedParticipant.DoesNotExist:
        return JsonResponse({"success": False, "message": "Participant not found."})


@admin_login_required
def participants_list(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    participants = quiz.allowed_participants.all().order_by("email")
    data = [{"email": p.email} for p in participants]
    return JsonResponse({"participants": data})


@admin_login_required
def download_allowed_emails(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    
    # User requested Download should follow LEADERBOARD order if participants exist
    leaderboard = calculate_quiz_scores(quiz)

    import csv
    from django.http import HttpResponse

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{quiz.name}_leaderboard_emails.csv"'

    writer = csv.writer(response)
    
    # Include Name and Email as requested
    writer.writerow(['Rank', 'Name', 'Email', 'Correct Answers', 'Final Score'])

    if leaderboard:
        # Export from performance
        for entry in leaderboard:
            writer.writerow([
                entry['rank'],
                entry['participant'].name,
                entry['participant'].email,
                entry['raw_score'],
                entry['final_score']
            ])
    else:
        # Fallback: Just return allowed emails if no one has taken the quiz but only if still in DRAFT?
        # Actually, let's just use the allowed list as fallback
        participants = quiz.allowed_participants.all().order_by("email")
        for p in participants:
            writer.writerow(['-', '-', p.email, '-', '-'])

    return response


# ------------------------------------------------------------------
# QUESTION MANAGEMENT
# ------------------------------------------------------------------

@admin_login_required
@require_http_methods(["POST"])
def question_create(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)

    if quiz.status != Quiz.Status.DRAFT:
        messages.error(request, "Cannot add questions after deployment.")
        return redirect("dashboard:quiz_manage", quiz_id=quiz_id)

    Question.objects.create(
        quiz=quiz,
        text=request.POST.get("text"),
        option_a=request.POST.get("option_a"),
        option_b=request.POST.get("option_b"),
        option_c=request.POST.get("option_c"),
        option_d=request.POST.get("option_d"),
        correct_option=request.POST.get("correct_option"),
        time_limit=int(request.POST.get("time_limit", 60)),
        order=int(request.POST.get("order", 1)),
    )

    messages.success(request, "Question added.")
    return redirect("dashboard:quiz_manage", quiz_id=quiz_id)


@admin_login_required
@require_http_methods(["POST"])
def question_delete(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    quiz_id = question.quiz.id

    if question.quiz.status != Quiz.Status.DRAFT:
        messages.error(request, "Cannot delete questions after deployment.")
        return redirect("dashboard:quiz_manage", quiz_id=quiz_id)

    question.delete()
    messages.success(request, "Question deleted.")
    return redirect("dashboard:quiz_manage", quiz_id=quiz_id)


# ------------------------------------------------------------------
# ADMIN LEADERBOARD (READ ONLY)
# ------------------------------------------------------------------

@admin_login_required
def quiz_leaderboard_view(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    leaderboard = calculate_quiz_scores(quiz)

    return render(
        request,
        "dashboard/quiz_leaderboard.html",
        {"quiz": quiz, "leaderboard": leaderboard},
    )


@admin_login_required
def quiz_live_leaderboard(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    leaderboard = calculate_quiz_scores(quiz)
    return render(request, "dashboard/live_leaderboard.html", {"quiz": quiz, "leaderboard": leaderboard})


@admin_login_required
def quiz_live_data(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    leaderboard = calculate_quiz_scores(quiz)

    # Format for JSON
    data = []
    for entry in leaderboard:
        data.append(
            {
                "rank": entry["rank"],
                "name": entry["participant"].name,
                "email": entry["participant"].email,
                "score": entry["final_score"],
                "raw_score": entry["raw_score"],
                "cheat_score": entry["cheat_score"],
                "penalty": entry["penalty"],
                "time": entry["total_time"],
            }
        )
    return JsonResponse(data, safe=False)


@admin_login_required
@require_http_methods(["POST"])
def question_upload_csv(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)

    if quiz.status != Quiz.Status.DRAFT:
        return JsonResponse({"success": False, "message": "Cannot upload questions for non-draft quizzes."})

    if "file" not in request.FILES:
        return JsonResponse({"success": False, "message": "No file uploaded."})

    csv_file = request.FILES["file"]
    try:
        data = TextIOWrapper(csv_file.file, encoding="utf-8")
        reader = csv.reader(data)
        next(reader)  # Skip header

        count = 0
        for row in reader:
            if not row or len(row) < 8:
                continue

            Question.objects.create(
                quiz=quiz,
                text=row[0].strip(),
                option_a=row[1].strip(),
                option_b=row[2].strip(),
                option_c=row[3].strip(),
                option_d=row[4].strip(),
                correct_option=row[5].strip().upper(),
                time_limit=int(row[6].strip()),
                order=int(row[7].strip()),
            )
            count += 1

        return JsonResponse({"success": True, "message": f"{count} questions uploaded successfully."})
    except Exception as e:
        return JsonResponse({"success": False, "message": f"Error uploading CSV: {e}"})

