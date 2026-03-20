import csv

from django.db.models import Case, Count, IntegerField, Sum, When
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.views.decorators.http import require_http_methods

from attempts.models import Attempt
from quizzes.models import Participant, Quiz


def calculate_quiz_scores(quiz):
    """Calculate leaderboard for a quiz (PostgreSQL-safe).

    Ranking:
    1) Final score (desc) [correct_answers - penalty]
    2) Total time taken (asc; lower is better)
    """

    scores = (
        Attempt.objects.filter(quiz=quiz)
        .values("participant")
        .annotate(
            total_score=Sum(
                Case(
                    When(is_correct=True, then=1),
                    default=0,
                    output_field=IntegerField(),
                )
            ),
            total_questions=Count("question"),
            total_time=Sum("time_taken"),
        )
    )

    participant_map = {
        p.id: p
        for p in Participant.objects.filter(id__in=[row["participant"] for row in scores])
    }

    raw_leaderboard = []
    for row in scores:
        participant = participant_map.get(row["participant"])
        if not participant:
            continue

        raw_score = int(row["total_score"] or 0)
        total_time = int(row["total_time"] or 0)
        
        cheat_score = participant.cheat_score
        penalty = cheat_score * 0.25
        final_score = round(raw_score - penalty, 2)
        if final_score < 0:
            final_score = 0.0

        raw_leaderboard.append({
            "participant": participant,
            "raw_score": raw_score,
            "cheat_score": cheat_score,
            "penalty": f"{penalty:.2f}",
            "final_score": f"{final_score:.2f}",
            "score": final_score,  # For internal sorting/logic
            "total_questions": int(row["total_questions"] or 0),
            "total_time": total_time,
        })

    # Sort by final_score DESC, total_time ASC
    raw_leaderboard.sort(key=lambda x: (-x["score"], x["total_time"]))

    leaderboard = []
    rank = 0
    prev_key = None

    for entry in raw_leaderboard:
        key = (entry["score"], entry["total_time"])
        if prev_key is None or key != prev_key:
            rank += 1
            prev_key = key

        entry["rank"] = rank
        leaderboard.append(entry)

    return leaderboard


def quiz_leaderboard(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    is_admin = request.session.get("is_admin")

    # 🔐 ACCESS CONTROL
    if not is_admin:
        # Check participant status based on cross-quiz email mapping
        participant_id = request.session.get("participant_id")
        if not participant_id:
             return redirect("core:landing")

        active_p = Participant.objects.filter(id=participant_id).first()
        if not active_p:
            return redirect("core:landing")

        participant = Participant.objects.filter(quiz=quiz, email=active_p.email).first()
        if not participant:
             return redirect("core:landing")

        # Rule: quiz.show_leaderboard must be True AND participant.has_completed must be True
        if not (quiz.show_leaderboard and participant.has_completed):
            return redirect("core:landing")

    leaderboard = calculate_quiz_scores(quiz)

    # Optional: fetch current participant's rank for highlighting
    participant_obj = None
    participant_rank = None
    if not is_admin:
        active_p = Participant.objects.filter(id=request.session.get("participant_id")).first()
        if active_p:
            target_p = Participant.objects.filter(quiz=quiz, email=active_p.email).first()
            if target_p:
                for entry in leaderboard:
                    if entry["participant"].id == target_p.id:
                        participant_rank = entry["rank"]
                        participant_obj = entry["participant"]
                        break

    return render(
        request,
        "leaderboard/quiz_leaderboard.html",
        {
            "quiz": quiz,
            "leaderboard": leaderboard,
            "participant": participant_obj,
            "participant_rank": participant_rank,
        },
    )


@require_http_methods(["GET"])
def download_csv(request, quiz_id):
    if not request.session.get("is_admin"):
        return redirect("dashboard:login")

    quiz = get_object_or_404(Quiz, id=quiz_id)

    leaderboard = calculate_quiz_scores(quiz)

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = (
        f'attachment; filename="quiz_{quiz.id}_leaderboard.csv"'
    )

    writer = csv.writer(response)
    writer.writerow(["Rank", "Name", "Email", "Correct Answers", "Cheat Count", "Penalty", "Final Score", "Questions", "Total Time (s)"])

    for entry in leaderboard:
        writer.writerow(
            [
                entry["rank"],
                entry["participant"].name,
                entry["participant"].email,
                entry["raw_score"],
                entry["cheat_score"],
                f"-{entry['penalty']}",
                entry["final_score"],
                entry["total_questions"],
                entry["total_time"],
            ]
        )

    return response


def final_podium(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)

    if not request.session.get("is_admin"):
        return redirect("dashboard:login")

    if quiz.status != Quiz.Status.ENDED:
        return HttpResponse("Quiz not ended yet", status=400)

    leaderboard = calculate_quiz_scores(quiz)
    podium = leaderboard[:3]

    while len(podium) < 3:
        podium.append(None)

    return render(request, "leaderboard/final_podium.html", {"quiz": quiz, "podium": podium})

