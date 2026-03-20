from django.db import models
from django.utils import timezone

from quizzes.models import Participant, Question, Quiz


class Attempt(models.Model):
    participant = models.ForeignKey(Participant, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)

    # Can be blank when server auto-submits on timeout (no selection).
    selected_option = models.CharField(max_length=1, null=True, blank=True)
    is_correct = models.BooleanField(default=False)
    time_taken = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("participant", "question")


class QuestionSession(models.Model):
    participant = models.ForeignKey(Participant, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)

    started_at = models.DateTimeField(null=True, blank=True)  # Set when question is first shown
    ended_at = models.DateTimeField(null=True, blank=True)
    order = models.IntegerField(default=0)  # Per-participant randomized order

    class Meta:
        unique_together = ("participant", "question")


class QuizAttempt(models.Model):
    participant = models.ForeignKey(Participant, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("participant", "quiz")
