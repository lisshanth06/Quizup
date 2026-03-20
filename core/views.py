from django.shortcuts import render
from django.http import JsonResponse
from quizzes.models import Quiz, Participant


def select_role(request):
    return render(request, "core/select_role.html")


def landing(request):
    """Landing page showing ALL LIVE quizzes."""
    live_quizzes = Quiz.objects.filter(status=Quiz.Status.LIVE).order_by('-created_at')
    
    # Identify user email from session
    user_email = None
    participant_id = request.session.get('participant_id')
    if participant_id:
        p = Participant.objects.filter(id=participant_id).first()
        if p:
            user_email = p.email

    quiz_list = []
    for quiz in live_quizzes:
        quiz.user_completed = False
        if user_email:
            # Check if this user completed this specific quiz
            participant = Participant.objects.filter(quiz=quiz, email=user_email).first()
            if participant and participant.has_completed:
                quiz.user_completed = True
        quiz_list.append(quiz)
    
    initial_states = {
        quiz.id: {
            'show_leaderboard': quiz.show_leaderboard,
            'is_active': quiz.is_active
        }
        for quiz in quiz_list
    }
    
    context = {
        'quizzes': quiz_list,
        'initial_states': initial_states,
    }
    
    return render(request, 'core/landing.html', context)


def quiz_state_api(request):
    """Returns lightweight quiz state as JSON so the user page can poll for changes."""
    live_quizzes = Quiz.objects.filter(status=Quiz.Status.LIVE).values(
        'id', 'name', 'show_leaderboard', 'is_active'
    )
    return JsonResponse(list(live_quizzes), safe=False)
