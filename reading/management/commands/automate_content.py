from django.core.management.base import BaseCommand
from django.db import transaction

from quiz.models import TextQuizAnswer, TextQuizQuestion
from reading.models import Text
from services.ai_engine import analyze_text_difficulty, generate_quiz_from_text


class Command(BaseCommand):
    help = "Populate missing text quizzes using the AI engine service."

    def add_arguments(self, parser):
        parser.add_argument("--limit", type=int, default=20)
        parser.add_argument("--dry-run", action="store_true")
        parser.add_argument("--overwrite", action="store_true")

    def handle(self, *args, **options):
        queryset = Text.objects.filter(status="published").order_by("level__order", "category__name", "title")
        if not options["overwrite"]:
            queryset = queryset.filter(quiz_questions__isnull=True)
        queryset = queryset.distinct()

        limit = options["limit"]
        if limit:
            queryset = queryset[:limit]

        processed = 0
        created_questions = 0

        for text in queryset:
            metrics = analyze_text_difficulty(text.content_en)
            questions = generate_quiz_from_text(text.content_en)
            processed += 1

            self.stdout.write(
                f"{text.slug}: suggested_level={metrics['suggested_level']} questions={len(questions)}"
            )

            if options["dry_run"]:
                continue

            with transaction.atomic():
                if options["overwrite"]:
                    text.quiz_questions.all().delete()

                for order, question_data in enumerate(questions[:5], start=1):
                    question = TextQuizQuestion.objects.create(
                        text=text,
                        question_text=question_data["question"],
                        order=order,
                        is_active=True,
                    )
                    TextQuizAnswer.objects.bulk_create(
                        [
                            TextQuizAnswer(
                                question=question,
                                answer_text=option["text"],
                                is_correct=option["is_correct"],
                            )
                            for option in question_data["options"][:4]
                        ]
                    )
                    created_questions += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Automation complete: {processed} text(s) processed; {created_questions} question(s) created."
            )
        )
