from django.conf import settings
from django.db import models


class ReadingProgress(models.Model):
    STATUS_CHOICES = [
        ("started", "Started"),
        ("completed", "Completed"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reading_progress",
    )
    text = models.ForeignKey(
        "reading.Text",
        on_delete=models.CASCADE,
        related_name="reading_progress",
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="started")
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    last_position = models.PositiveIntegerField(default=0)
    coins_awarded = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["-started_at"]
        unique_together = ["user", "text"]

    def __str__(self):
        return f"{self.user.get_username()} - {self.text.title}"


class FavoriteText(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="favorite_texts",
    )
    text = models.ForeignKey(
        "reading.Text",
        on_delete=models.CASCADE,
        related_name="favorited_by",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        unique_together = ["user", "text"]

    def __str__(self):
        return f"{self.user.get_username()} favoritou {self.text.title}"


class CoinTransaction(models.Model):
    REASON_CHOICES = [
        ("reading_completed", "Reading completed"),
        ("quiz_answer", "Quiz answer"),
        ("quiz_bonus", "Quiz bonus"),
        ("reread", "Reread"),
        ("achievement", "Achievement"),
        ("avatar_purchase", "Avatar purchase"),
        ("adjustment", "Adjustment"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="coin_transactions",
    )
    amount = models.IntegerField()
    reason = models.CharField(max_length=40, choices=REASON_CHOICES)
    related_text = models.ForeignKey(
        "reading.Text",
        on_delete=models.SET_NULL,
        related_name="coin_transactions",
        blank=True,
        null=True,
    )
    related_quiz_attempt = models.ForeignKey(
        "quiz.TextQuizAttempt",
        on_delete=models.SET_NULL,
        related_name="coin_transactions",
        blank=True,
        null=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.get_username()} {self.amount} ({self.reason})"


class Achievement(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, unique=True)
    description_pt = models.TextField(blank=True)
    icon = models.FileField(upload_to="achievements/", blank=True)
    coin_reward = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class UserAchievement(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="achievements",
    )
    achievement = models.ForeignKey(
        Achievement,
        on_delete=models.CASCADE,
        related_name="earned_by",
    )
    earned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-earned_at"]
        unique_together = ["user", "achievement"]

    def __str__(self):
        return f"{self.user.get_username()} - {self.achievement.name}"
