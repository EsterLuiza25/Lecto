from django.test import TestCase
from django.urls import reverse

from reading.models import Category, Level
from .models import PlacementQuizAnswer, PlacementQuizQuestion


class PlacementQuizFilteringTests(TestCase):
    def setUp(self):
        self.level = Level.objects.create(
            name="Iniciante",
            slug="iniciante",
            order=1,
            min_words=40,
            max_words=80,
        )
        self.anime = Category.objects.create(name="Anime", slug="anime", is_active=True)
        self.cotidiano = Category.objects.create(name="Cotidiano", slug="cotidiano", is_active=True)

        self.general_question = self.create_question("General beginner question", None, 1)
        self.anime_question = self.create_question("Anime beginner question", self.anime, 2)
        self.cotidiano_question = self.create_question("Cotidiano beginner question", self.cotidiano, 3)

    def create_question(self, text, category, order):
        question = PlacementQuizQuestion.objects.create(
            target_level=self.level,
            category=category,
            question_text=text,
            order=order,
            is_active=True,
        )
        PlacementQuizAnswer.objects.create(question=question, answer_text="Correct", is_correct=True)
        PlacementQuizAnswer.objects.create(question=question, answer_text="Wrong", is_correct=False)
        return question

    def test_specific_category_uses_level_and_category_intersection(self):
        response = self.client.get(
            reverse("quiz:placement_start"),
            {"nivel": "iniciante", "categoria": "cotidiano"},
        )

        questions = list(response.context["questions"])

        self.assertEqual(questions, [self.cotidiano_question])
        self.assertEqual(response.context["selected_level"], self.level)
        self.assertEqual(response.context["selected_category"], self.cotidiano)

    def test_empty_category_uses_general_level_questions_only(self):
        response = self.client.get(
            reverse("quiz:placement_start"),
            {"nivel": "iniciante", "categoria": ""},
        )

        questions = list(response.context["questions"])

        self.assertEqual(questions, [self.general_question])
        self.assertIsNone(response.context["selected_category"])

    def test_specific_category_without_questions_does_not_fallback_to_general(self):
        self.cotidiano_question.delete()

        response = self.client.get(
            reverse("quiz:placement_start"),
            {"nivel": "iniciante", "categoria": "cotidiano"},
        )

        self.assertEqual(list(response.context["questions"]), [])
        self.assertContains(response, "Ainda nao existem perguntas para esse nivel e categoria.")
