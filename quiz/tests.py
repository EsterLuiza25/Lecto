from django.test import TestCase
from django.urls import reverse

from reading.models import Category, Level, Text
from .models import PlacementQuizAnswer, PlacementQuizQuestion, TextQuizAnswer, TextQuizQuestion


class PlacementQuizFilteringTests(TestCase):
    def setUp(self):
        self.level = Level.objects.create(
            name="Iniciante",
            slug="iniciante",
            order=1,
            min_words=40,
            max_words=80,
        )
        self.a1 = Level.objects.create(
            name="A1",
            slug="a1",
            order=2,
            min_words=80,
            max_words=120,
        )
        self.anime = Category.objects.create(name="Anime", slug="anime", is_active=True)
        self.cotidiano = Category.objects.create(name="Cotidiano", slug="cotidiano", is_active=True)

        self.general_question = self.create_question("General beginner question", None, 1)
        self.a1_general_question = self.create_question("General A1 question", None, 1, level=self.a1)
        self.anime_question = self.create_question("Anime beginner question", self.anime, 2)
        self.cotidiano_question = self.create_question("Cotidiano beginner question", self.cotidiano, 3)

    def create_question(self, text, category, order, level=None):
        question = PlacementQuizQuestion.objects.create(
            target_level=level or self.level,
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

    def test_diagnostic_mode_uses_general_questions_from_multiple_levels(self):
        response = self.client.get(reverse("quiz:placement_start"), {"modo": "diagnostico"})

        questions = list(response.context["questions"])

        self.assertTrue(response.context["is_diagnostic"])
        self.assertEqual(questions, [self.general_question, self.a1_general_question])
        self.assertIsNone(response.context["selected_level"])
        self.assertIsNone(response.context["selected_category"])

    def test_diagnostic_mode_recommends_level_from_score(self):
        correct_beginner = self.general_question.answers.get(is_correct=True)
        correct_a1 = self.a1_general_question.answers.get(is_correct=True)

        response = self.client.post(
            reverse("quiz:placement_start"),
            {
                "modo": "diagnostico",
                f"question_{self.general_question.id}": correct_beginner.id,
                f"question_{self.a1_general_question.id}": correct_a1.id,
            },
        )

        result = response.context["result"]

        self.assertTrue(result["is_diagnostic"])
        self.assertEqual(result["score"], 2)
        self.assertEqual(result["recommended_level"], self.a1)
        self.assertEqual(len(result["question_results"]), 2)
        self.assertContains(response, "Nivel indicado: A1")
        self.assertContains(response, "answer-review")
        self.assertContains(response, "Acertou")
        self.assertContains(response, "Refazer teste")
        self.assertNotContains(response, "Ver resultado")

    def test_placement_result_shows_wrong_answer_and_correct_answer(self):
        wrong_answer = self.cotidiano_question.answers.get(is_correct=False)
        correct_answer = self.cotidiano_question.answers.get(is_correct=True)

        response = self.client.post(
            reverse("quiz:placement_start"),
            {
                "nivel": "iniciante",
                "categoria": "cotidiano",
                f"question_{self.cotidiano_question.id}": wrong_answer.id,
            },
        )

        self.assertContains(response, "Errou")
        self.assertContains(response, f"Sua resposta: {wrong_answer.answer_text}")
        self.assertContains(response, f"Resposta correta: {correct_answer.answer_text}")


class TextQuizFeedbackTests(TestCase):
    def setUp(self):
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
            content_en="Rio reads a short note and understands the problem.",
            level=self.level,
            category=self.category,
            status="published",
        )
        self.question = TextQuizQuestion.objects.create(
            text=self.text,
            question_text="What does Rio understand?",
            order=1,
            is_active=True,
        )
        self.correct_answer = TextQuizAnswer.objects.create(
            question=self.question,
            answer_text="The problem",
            is_correct=True,
        )
        self.wrong_answer = TextQuizAnswer.objects.create(
            question=self.question,
            answer_text="The weather",
            is_correct=False,
        )

    def test_text_quiz_result_shows_answer_feedback(self):
        response = self.client.post(
            reverse("quiz:text_quiz", args=[self.text.slug]),
            {f"question_{self.question.id}": self.wrong_answer.id},
        )

        result = response.context["result"]

        self.assertEqual(result["score"], 0)
        self.assertEqual(len(result["question_results"]), 1)
        self.assertContains(response, "Errou")
        self.assertContains(response, f"Sua resposta: {self.wrong_answer.answer_text}")
        self.assertContains(response, f"Resposta correta: {self.correct_answer.answer_text}")
