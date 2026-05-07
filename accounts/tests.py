from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from progress.models import CoinTransaction, ReadingProgress
from reading.models import Category, Level, Text

from .models import AvatarOption, UserAvatarUnlock, UserProfile


class AvatarShopUnlockTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="ester", password="123")
        self.profile = self.user.profile
        self.profile.coin_balance = 100
        self.profile.save(update_fields=["coin_balance"])
        self.level = Level.objects.create(name="Iniciante", slug="iniciante", order=1)
        self.tech = Category.objects.create(name="Tecnologia", slug="tecnologia", is_active=True)
        self.games = Category.objects.create(name="Games", slug="games", is_active=True)
        self.option = AvatarOption.objects.create(
            name="Fones Tecnologia",
            option_type="accessory",
            coin_price=10,
            required_category=self.tech,
            required_category_reads=2,
            is_active=True,
        )

    def make_text(self, slug, category):
        return Text.objects.create(
            title=slug.replace("-", " ").title(),
            slug=slug,
            summary_pt="Resumo",
            content_en="A short text for testing.",
            level=self.level,
            category=category,
            status="published",
        )

    def complete(self, slug, category):
        ReadingProgress.objects.create(
            user=self.user,
            text=self.make_text(slug, category),
            status="completed",
        )

    def test_category_requirement_uses_only_matching_category_reads(self):
        self.complete("tech-1", self.tech)
        self.complete("games-1", self.games)

        status = self.option.unlock_status_for(self.user)
        self.assertFalse(status["meets_read_requirement"])
        self.assertEqual(status["reads_done"], 1)
        self.assertEqual(status["reads_missing"], 1)

        self.complete("tech-2", self.tech)
        status = self.option.unlock_status_for(self.user)
        self.assertTrue(status["meets_read_requirement"])
        self.assertTrue(status["can_unlock"])

    def test_purchase_endpoint_rejects_insufficient_coins_with_missing_amount(self):
        option = AvatarOption.objects.create(
            name="Cachecol caro",
            option_type="outfit",
            coin_price=120,
            is_active=True,
        )
        self.client.force_login(self.user)

        response = self.client.post(reverse("avatar_purchase", args=[option.id]))

        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json()["ok"])
        self.assertIn("Faltam 20", response.json()["error"])
        self.assertFalse(UserAvatarUnlock.objects.filter(user=self.user, option=option).exists())

    def test_purchase_endpoint_unlocks_item_and_debits_coins(self):
        self.complete("tech-1", self.tech)
        self.complete("tech-2", self.tech)
        self.client.force_login(self.user)

        response = self.client.post(reverse("avatar_purchase", args=[self.option.id]))

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["ok"])
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.coin_balance, 90)
        self.assertTrue(UserAvatarUnlock.objects.filter(user=self.user, option=self.option).exists())
        self.assertTrue(
            CoinTransaction.objects.filter(
                user=self.user,
                amount=-10,
                reason="avatar_purchase",
            ).exists()
        )
