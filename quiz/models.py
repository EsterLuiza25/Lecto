from django.conf import settings
from django.db import models


class PlacementQuizQuestion(models.Model):
    target_level = models.ForeignKey(
        "reading.Level",
        on_delete=models.CASCADE,
        related_name="placement_questions",
    )
    category = models.ForeignKey(
        "reading.Category",
        on_delete=models.SET_NULL,
        related_name="placement_questions",
        blank=True,
        null=True,
    )
    question_text = models.TextField()
    order = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["target_level__order", "category__name", "order"]

    def __str__(self):
        return f"{self.target_level}: {self.question_text[:60]}"


class PlacementQuizAnswer(models.Model):
    question = models.ForeignKey(
        PlacementQuizQuestion,
        on_delete=models.CASCADE,
        related_name="answers",
    )
    answer_text = models.CharField(max_length=240)
    is_correct = models.BooleanField(default=False)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return self.answer_text


class QuizAttempt(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="placement_quiz_attempts",
        blank=True,
        null=True,
    )
    target_level = models.ForeignKey(
        "reading.Level",
        on_delete=models.PROTECT,
        related_name="quiz_attempts",
    )
    category = models.ForeignKey(
        "reading.Category",
        on_delete=models.SET_NULL,
        related_name="quiz_attempts",
        blank=True,
        null=True,
    )
    score = models.PositiveSmallIntegerField(default=0)
    total_questions = models.PositiveSmallIntegerField(default=7)
    percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    recommended_level = models.ForeignKey(
        "reading.Level",
        on_delete=models.SET_NULL,
        related_name="placement_recommendations",
        blank=True,
        null=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.target_level} - {self.score}/{self.total_questions}"

    @property
    def passed(self):
        return self.score >= 5


class TextQuizQuestion(models.Model):
    text = models.ForeignKey(
        "reading.Text",
        on_delete=models.CASCADE,
        related_name="quiz_questions",
    )
    question_text = models.TextField()
    order = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["text", "order"]

    def __str__(self):
        return f"{self.text.title}: {self.question_text[:60]}"


class TextQuizAnswer(models.Model):
    question = models.ForeignKey(
        TextQuizQuestion,
        on_delete=models.CASCADE,
        related_name="answers",
    )
    answer_text = models.CharField(max_length=240)
    is_correct = models.BooleanField(default=False)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return self.answer_text


class TextQuizAttempt(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="text_quiz_attempts",
    )
    text = models.ForeignKey(
        "reading.Text",
        on_delete=models.CASCADE,
        related_name="quiz_attempts",
    )
    score = models.PositiveSmallIntegerField(default=0)
    total_questions = models.PositiveSmallIntegerField(default=5)
    percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    coins_awarded = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.get_username()} - {self.text.title} - {self.score}/{self.total_questions}"
