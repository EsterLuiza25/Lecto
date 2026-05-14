import json

from django.test import TestCase
from django.urls import reverse

from quiz.models import TextQuizAnswer, TextQuizQuestion
from reading.models import Category, Level, Text, VocabularyItem


class ApiV1Tests(TestCase):
    def setUp(self):
        self.level = Level.objects.create(
            name="Iniciante",
            slug="iniciante",
            order=1,
            min_words=40,
            max_words=80,
        )
        self.category = Category.objects.create(name="Tecnologia", slug="tecnologia", is_active=True)
        self.text = Text.objects.create(
            title="A Friendly Robot",
            slug="a-friendly-robot",
            summary_pt="Um robo amigavel.",
            content_en="A robot helps Ana. It reads a note and smiles.",
            level=self.level,
            category=self.category,
            status="published",
        )
        VocabularyItem.objects.create(
            text=self.text,
            word_en="robot",
            lemma_en="robot",
            part_of_speech="noun",
            translation_pt="robo",
            pronunciation_pt="ROU-bot",
            example_en="A robot helps Ana.",
            order=1,
        )
        question = TextQuizQuestion.objects.create(
            text=self.text,
            question_text="Who helps Ana?",
            order=1,
            is_active=True,
        )
        TextQuizAnswer.objects.create(question=question, answer_text="A robot", is_correct=True)
        TextQuizAnswer.objects.create(question=question, answer_text="A cat", is_correct=False)

    def test_texts_endpoint_returns_json(self):
        response = self.client.get(reverse("api_v1:text-list"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")
        self.assertEqual(response.json()[0]["slug"], self.text.slug)

    def test_vocabulary_endpoint_can_filter_by_text(self):
        response = self.client.get(reverse("api_v1:vocabulary-list"), {"text": self.text.slug})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()[0]["word_en"], "robot")

    def test_text_quiz_endpoint_returns_answers(self):
        response = self.client.get(reverse("api_v1:text-quiz-list"), {"text": self.text.slug})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()[0]["answers"][0]["answer_text"], "A robot")

    def test_ai_explain_endpoint_uses_text_vocabulary(self):
        response = self.client.post(
            reverse("api_v1:ai-explain"),
            {
                "selection": "A robot helps Ana.",
                "text_slug": self.text.slug,
            },
            content_type="application/json",
        )

        payload = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(payload["source"], "local_fallback")
        self.assertIn("robo", payload["explanation_pt"])

    def test_openapi_schema_endpoint_is_available(self):
        response = self.client.get(reverse("api_v1:schema"), HTTP_ACCEPT="application/json")

        self.assertEqual(response.status_code, 200)
        payload = json.loads(response.content)
        self.assertIn("openapi", payload)

    def test_swagger_ui_endpoint_is_available(self):
        response = self.client.get(reverse("api_v1:swagger-ui"))

        self.assertEqual(response.status_code, 200)
        self.assertIn("text/html", response["Content-Type"])
