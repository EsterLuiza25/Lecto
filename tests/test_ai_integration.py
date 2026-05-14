from unittest.mock import patch

from django.test import TestCase

from reading.management.commands.automate_content import Command
from reading.models import Category, Level, Text
from quiz.models import TextQuizQuestion
from services.ai_engine import analyze_text_difficulty, explain_selection, generate_quiz_from_text


class AIEngineIntegrationTests(TestCase):
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

    def test_ai_engine_fallback_generates_quiz_shape(self):
        quiz = generate_quiz_from_text(self.text.content_en)

        self.assertEqual(len(quiz), 5)
        self.assertIn("question", quiz[0])
        self.assertEqual(len(quiz[0]["options"]), 4)
        self.assertTrue(any(option["is_correct"] for option in quiz[0]["options"]))

    def test_ai_engine_analyzes_text_difficulty(self):
        metrics = analyze_text_difficulty(self.text.content_en)

        self.assertEqual(metrics["suggested_level"], "Iniciante")
        self.assertGreater(metrics["word_count"], 0)

    def test_ai_engine_local_explanation_uses_specific_translation(self):
        explanation = explain_selection(
            "There is a tea on a small table.",
            glossary={"tea": "cha", "table": "mesa"},
        )

        self.assertEqual(explanation["source"], "local_fallback")
        self.assertIn("Traducao aproximada", explanation["explanation_pt"])
        self.assertIn("cha", explanation["explanation_pt"])
        self.assertIn("mesa", explanation["explanation_pt"])
        self.assertIn("There is", explanation["grammar_note_pt"])

    def test_automation_command_uses_ai_engine_to_create_quiz(self):
        mocked_quiz = [
            {
                "question": f"Question {index}?",
                "options": [
                    {"text": "Correct", "is_correct": True},
                    {"text": "Wrong A", "is_correct": False},
                    {"text": "Wrong B", "is_correct": False},
                    {"text": "Wrong C", "is_correct": False},
                ],
            }
            for index in range(1, 6)
        ]

        with patch("reading.management.commands.automate_content.generate_quiz_from_text", return_value=mocked_quiz):
            Command().handle(limit=1, dry_run=False, overwrite=False)

        self.assertEqual(TextQuizQuestion.objects.filter(text=self.text).count(), 5)
