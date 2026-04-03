from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_http_methods
from django.views.decorators.cache import never_cache
from django.utils import timezone
from random import shuffle

from .models import Quiz, Question, Participant, AllowedParticipant
from attempts.models import Attempt, QuestionSession, QuizAttempt


# =====================================================
# QUIZ DETAIL — SERVER SIDE TIMER + RANDOMIZED ORDER
# =====================================================
@never_cache
def quiz_detail(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)

    if quiz.status != Quiz.Status.LIVE:
        return render(request, 'quizzes/quiz_waiting.html', {
            'quiz': quiz,
            'participant': None
        })

    # 🔐 Must be logged in via OTP
    participant_id = request.session.get('participant_id')
    if not participant_id:
        return redirect('accounts:send_otp', quiz_id=quiz.id)

    participant = get_object_or_404(
        Participant,
        id=participant_id,
        quiz=quiz
    )

    # 🚫 Must be verified
    if not participant.verified:
        request.session.flush()
        return redirect('accounts:send_otp', quiz_id=quiz.id)

    # 🚫 Cannot re-attempt the quiz once completed
    if QuizAttempt.objects.filter(participant=participant, quiz=quiz).exists() or participant.has_completed:
        return redirect('quizzes:quiz_submitted', quiz_id=quiz.id)

    # 🚫 Wait if not properly started
    if not quiz.is_active:
        return redirect('quizzes:quiz_waiting', quiz_id=quiz.id)

    # -------------------------------------------------
    # 🔀 RANDOMIZE ONCE — Generate sessions if first visit
    # -------------------------------------------------
    existing_sessions_count = QuestionSession.objects.filter(
        participant=participant,
        quiz=quiz
    ).count()
    total_questions = quiz.questions.count()

    if existing_sessions_count == 0 and total_questions > 0:
        # First time — shuffle and persist order for this participant
        questions = list(quiz.questions.all())
        shuffle(questions)
        sessions_to_create = []
        for index, q in enumerate(questions):
            sessions_to_create.append(
                QuestionSession(
                    participant=participant,
                    quiz=quiz,
                    question=q,
                    order=index,
                )
            )
        QuestionSession.objects.bulk_create(sessions_to_create)

    # -------------------------------------------------
    # 🔐 Get FIRST unanswered question in participant's order
    # -------------------------------------------------
    ordered_sessions = QuestionSession.objects.filter(
        participant=participant,
        quiz=quiz
    ).order_by('order').select_related('question')

    current_question = None
    question_session = None
    question_no = 0

    for idx, qs_item in enumerate(ordered_sessions, start=1):
        if not Attempt.objects.filter(
            participant=participant,
            question=qs_item.question
        ).exists():
            current_question = qs_item.question
            question_session = qs_item
            question_no = idx
            break

    # ✅ All questions completed → submission page
    if not current_question:
        QuizAttempt.objects.get_or_create(participant=participant, quiz=quiz)
        if not participant.has_completed:
            participant.has_completed = True
            participant.save(update_fields=['has_completed'])
        return redirect('quizzes:quiz_submitted', quiz_id=quiz.id)

    # ⏱ Activate timer on first view of this question
    # started_at is None when created via bulk_create (not yet shown to user)
    if question_session.started_at is None:
        question_session.started_at = timezone.now()
        question_session.save(update_fields=['started_at'])

    # -------------------------------------------------
    # ⏱ SERVER CALCULATED REMAINING TIME
    # -------------------------------------------------
    elapsed = (timezone.now() - question_session.started_at).total_seconds()
    remaining_time = max(0, current_question.time_limit - int(elapsed))

    # ⛔ Time expired → server-side auto-save
    if remaining_time == 0:
        Attempt.objects.get_or_create(
            participant=participant,
            quiz=quiz,
            question=current_question,
            defaults={
                'selected_option': None,
                'is_correct': False,
                'time_taken': int(current_question.time_limit),
            }
        )
        question_session.ended_at = timezone.now()
        question_session.save(update_fields=["ended_at"])
        return redirect('quizzes:quiz_detail', quiz_id=quiz.id)

    return render(request, 'quizzes/quiz_detail.html', {
        'quiz': quiz,
        'participant': participant,
        'question': current_question,
        'remaining_time': int(remaining_time),
        'question_no': question_no,
        'total_questions': total_questions,
    })


# =====================================================
# SUBMIT ANSWER — SERVER ENFORCED
# =====================================================
@require_http_methods(["POST"])
def submit_answer(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)

    participant_id = request.session.get('participant_id')
    if not participant_id:
        return redirect('accounts:send_otp', quiz_id=quiz.id)

    participant = get_object_or_404(
        Participant,
        id=participant_id,
        quiz=quiz
    )

    if quiz.status != Quiz.Status.LIVE:
        return redirect('quizzes:quiz_submitted', quiz_id=quiz.id)

    # 🚫 Already completed this quiz
    if QuizAttempt.objects.filter(participant=participant, quiz=quiz).exists() or participant.has_completed:
        return redirect('quizzes:quiz_submitted', quiz_id=quiz.id)

    # 🔐 Get current question from participant's personal session order
    ordered_sessions = QuestionSession.objects.filter(
        participant=participant,
        quiz=quiz
    ).order_by('order').select_related('question')

    question = None
    qs = None
    for session in ordered_sessions:
        if not Attempt.objects.filter(
            participant=participant,
            question=session.question
        ).exists():
            question = session.question
            qs = session
            break

    if not qs or not question:
        return redirect('quizzes:quiz_detail', quiz_id=quiz.id)

    if qs.started_at is None:
        return redirect('quizzes:quiz_detail', quiz_id=quiz.id)

    elapsed = (timezone.now() - qs.started_at).total_seconds()

    # ⛔ TIME EXPIRED (server decides)
    if elapsed > question.time_limit:
        selected = None
        is_correct = False
        time_taken = question.time_limit
    else:
        selected = request.POST.get('option') or None
        is_correct = (selected == question.correct_option)
        time_taken = int(elapsed)

    # ❌ Prevent duplicate submission
    Attempt.objects.get_or_create(
        participant=participant,
        quiz=quiz,
        question=question,
        defaults={
            'selected_option': selected,
            'is_correct': is_correct,
            'time_taken': time_taken
        }
    )

    # ⏹ Close question session
    qs.ended_at = timezone.now()
    qs.save(update_fields=["ended_at"])

    # ➡️ Move to next question
    return redirect('quizzes:quiz_detail', quiz_id=quiz.id)


# =====================================================
# QUIZ WAITING PAGE
# =====================================================
def quiz_waiting(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)

    if quiz.is_active:
        return redirect('quizzes:quiz_detail', quiz_id=quiz.id)

    participant = None
    if request.session.get('participant_id'):
        participant = Participant.objects.filter(
            id=request.session['participant_id'],
            quiz=quiz
        ).first()

    return render(request, 'quizzes/quiz_waiting.html', {
        'quiz': quiz,
        'participant': participant
    })


# =====================================================
# QUIZ SUBMITTED PAGE
# =====================================================
def quiz_submitted(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)

    if not request.session.get('participant_id'):
        return redirect('core:landing')

    return render(request, 'quizzes/quiz_submitted.html', {
        'quiz': quiz
    })


# =====================================================
# QUIZ RULES PAGE
# =====================================================
def quiz_rules(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    return render(request, 'quizzes/rules.html', {
        'quiz': quiz
    })


# =====================================================
# ANTI-CHEAT REPORTING
# =====================================================
import json
from django.http import JsonResponse

@never_cache
@require_http_methods(["POST"])
def report_cheat(request, quiz_id):
    participant_id = request.session.get('participant_id')
    if not participant_id:
        return JsonResponse({"error": "Unauthorized"}, status=401)

    try:
        participant = Participant.objects.get(id=participant_id, quiz_id=quiz_id)
        
        # Parse reason optionally
        try:
            data = json.loads(request.body)
            reason = data.get("reason", "Unknown")
            print(f"Cheat detected for {participant.email}: {reason}")
        except:
            pass
            
        participant.cheat_score += 1
        participant.save(update_fields=['cheat_score'])
        
        return JsonResponse({"success": True, "new_score": participant.cheat_score})
    except Participant.DoesNotExist:
        return JsonResponse({"error": "Participant not found"}, status=404)
