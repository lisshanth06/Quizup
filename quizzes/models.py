import uuid

from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone


class Quiz(models.Model):
    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        LIVE = "LIVE", "Live"
        ENDED = "ENDED", "Ended"

    name = models.CharField(max_length=255)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.DRAFT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    slug = models.SlugField(unique=True, blank=True)
    show_leaderboard = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = uuid.uuid4().hex[:8]
        super().save(*args, **kwargs)

    def can_edit(self):
        return self.status == self.Status.DRAFT

    def deploy(self):
        if self.status == self.Status.DRAFT:
            self.status = self.Status.LIVE
            self.save(update_fields=["status", "updated_at"])

    def end(self):
        if self.status == self.Status.LIVE:
            self.status = self.Status.ENDED
            self.save(update_fields=["status", "updated_at"])


class AllowedParticipant(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="allowed_participants")
    email = models.EmailField(max_length=254)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [["quiz", "email"]]

    def __str__(self):
        return f"{self.email} (Allowed for {self.quiz.name})"


class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="questions")
    text = models.TextField(null=True, blank=True)
    option_a = models.CharField(max_length=500)
    option_b = models.CharField(max_length=500)
    option_c = models.CharField(max_length=500)
    option_d = models.CharField(max_length=500)
    correct_option = models.CharField(
        max_length=1, choices=[("A", "A"), ("B", "B"), ("C", "C"), ("D", "D")]
    )
    time_limit = models.PositiveIntegerField(default=60, validators=[MinValueValidator(10)])
    order = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"Question {self.order} - {self.quiz.name}"


class Participant(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="participants")
    name = models.CharField(max_length=255)
    email = models.EmailField(max_length=254)
    has_completed = models.BooleanField(default=False)
    cheat_score = models.IntegerField(default=0)

    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [["quiz", "email"]]

    def __str__(self):
        return f"{self.name} - {self.email}"

