from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from accounts.models import UserProfile
from reading.models import Category, Level, Text

from .models import Achievement
from .services import process_completed_reading


class ReadingGamificationServiceTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="ester", password="123")
        self.level = Level.objects.create(name="Iniciante", slug="iniciante", order=1)
        self.category = Category.objects.create(name="Tecnologia", slug="tecnologia", is_active=True)

    def make_text(self, index):
        return Text.objects.create(
            title=f"Texto {index}",
            slug=f"texto-{index}",
            summary_pt="Resumo",
            content_en="A short text for testing.",
            level=self.level,
            category=self.category,
            status="published",
        )

    def test_completed_reading_updates_coins_and_streak(self):
        first_at = timezone.now() - timedelta(days=2)
        second_at = first_at + timedelta(hours=23)
        late_at = second_at + timedelta(hours=25)

        process_completed_reading(self.user, self.make_text(1), completed_at=first_at)
        process_completed_reading(self.user, self.make_text(2), completed_at=second_at)
        profile = UserProfile.objects.get(user=self.user)
        self.assertEqual(profile.reading_streak, 2)
        self.assertEqual(profile.longest_reading_streak, 2)
        self.assertEqual(profile.coin_balance, 10)

        process_completed_reading(self.user, self.make_text(3), completed_at=late_at)
        profile.refresh_from_db()
        self.assertEqual(profile.reading_streak, 1)
        self.assertEqual(profile.longest_reading_streak, 2)
        self.assertEqual(profile.coin_balance, 15)

    def test_badges_are_awarded_at_total_reading_milestones(self):
        for index in range(1, 11):
            process_completed_reading(self.user, self.make_text(index), completed_at=timezone.now())

        self.assertTrue(
            Achievement.objects.filter(slug="leitor-bronze", earned_by__user=self.user).exists()
        )
