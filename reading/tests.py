from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from progress.models import ReadingProgress
from quiz.models import TextQuizAttempt
from reading.models import Category, Level, Text


class TextCompletionRequiresQuizTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="leitora",
            password="senha-segura",
        )
        self.level = Level.objects.create(
            name="Iniciante",
            slug="iniciante",
            order=1,
            min_words=40,
            max_words=80,
        )
        self.category = Category.objects.create(name="Cotidiano", slug="cotidiano", is_active=True)
        self.text = Text.objects.create(
            title="A Simple Day",
            slug="a-simple-day",
            summary_pt="Um dia simples.",
            content_en="Rio reads a short note.",
            level=self.level,
            category=self.category,
            status="published",
        )

    def test_detail_requires_text_quiz_before_completion(self):
        self.client.force_login(self.user)

        response = self.client.get(self.text.get_absolute_url())

        self.assertContains(response, "Responder quiz para liberar recompensa")
        self.assertNotContains(response, "Concluir leitura (+5 moedinhas)")

    def test_mark_completed_redirects_to_quiz_without_attempt(self):
        self.client.force_login(self.user)

        response = self.client.post(reverse("reading:mark_completed", args=[self.text.slug]))

        self.assertRedirects(response, reverse("quiz:text_quiz", args=[self.text.slug]))
        self.assertFalse(
            ReadingProgress.objects.filter(user=self.user, text=self.text, status="completed").exists()
        )

    def test_mark_completed_is_unlocked_after_text_quiz_attempt(self):
        self.client.force_login(self.user)
        TextQuizAttempt.objects.create(
            user=self.user,
            text=self.text,
            score=4,
            total_questions=5,
            percentage=Decimal("80.00"),
            coins_awarded=9,
        )

        detail_response = self.client.get(self.text.get_absolute_url())
        self.assertContains(detail_response, "Concluir leitura (+5 moedinhas)")

        response = self.client.post(reverse("reading:mark_completed", args=[self.text.slug]))

        self.assertRedirects(response, self.text.get_absolute_url())
        progress = ReadingProgress.objects.get(user=self.user, text=self.text)
        self.assertEqual(progress.status, "completed")
        self.assertEqual(progress.coins_awarded, 5)
