import re

from django.core.management.base import BaseCommand

from quiz.models import PlacementQuizAnswer, PlacementQuizQuestion
from reading.models import Category, Level, Text


SENTENCE_RE = re.compile(r"(?<=[.!?])\s+")


class Command(BaseCommand):
    help = "Create category-specific placement quiz questions for every active category and level."

    def add_arguments(self, parser):
        parser.add_argument(
            "--include-general",
            action="store_true",
            help="Also recreate the generic placement quizzes from published texts.",
        )

    def handle(self, *args, **options):
        deleted, _ = PlacementQuizQuestion.objects.filter(category__isnull=False).delete()
        self.stdout.write(f"Deleted {deleted} category-specific placement questions/answers.")

        total = 0
        missing = []
        levels = Level.objects.order_by("order")
        categories = Category.objects.filter(is_active=True).order_by("name")

        if options["include_general"]:
            deleted_general, _ = PlacementQuizQuestion.objects.filter(category__isnull=True).delete()
            self.stdout.write(f"Deleted {deleted_general} generic placement questions/answers.")
            for level in levels:
                texts = list(self.texts_for(level=level, category=None)[:7])
                total += self.create_questions(level, None, texts)
                if len(texts) < 7:
                    missing.append(f"{level.slug} / geral: {len(texts)} texts")

        for level in levels:
            for category in categories:
                texts = list(self.texts_for(level=level, category=category)[:7])
                total += self.create_questions(level, category, texts)
                if len(texts) < 7:
                    missing.append(f"{level.slug} / {category.slug}: {len(texts)} texts")

        if missing:
            self.stdout.write(self.style.WARNING("Intersections with fewer than 7 source texts:"))
            for item in missing:
                self.stdout.write(self.style.WARNING(item))

        self.stdout.write(self.style.SUCCESS(f"Created {total} placement quiz questions."))

    def texts_for(self, level, category):
        queryset = Text.objects.filter(level=level, status="published").order_by("category__name", "title")
        if category is not None:
            queryset = queryset.filter(category=category)
        return queryset

    def create_questions(self, level, category, texts):
        if not texts:
            return 0

        title_options = [text.title for text in texts]
        created = 0

        for order, text in enumerate(texts, start=1):
            snippet = self.snippet_for(text.content_en)
            question = PlacementQuizQuestion.objects.create(
                target_level=level,
                category=category,
                question_text=f'Leia: "{snippet}" Qual e o melhor titulo para esse trecho?',
                order=order,
                is_active=True,
            )
            options = self.answer_options(
                correct=text.title,
                pool=title_options,
                level=level,
                category=category,
                order=order,
            )
            PlacementQuizAnswer.objects.bulk_create(
                [
                    PlacementQuizAnswer(
                        question=question,
                        answer_text=answer_text,
                        is_correct=is_correct,
                    )
                    for answer_text, is_correct in options
                ]
            )
            created += 1

        return created

    def snippet_for(self, content):
        sentences = [sentence.strip() for sentence in SENTENCE_RE.split(content or "") if sentence.strip()]
        snippet = " ".join(sentences[:2])
        words = snippet.split()
        if len(words) > 34:
            snippet = " ".join(words[:34]) + "..."
        return snippet

    def answer_options(self, correct, pool, level, category, order):
        distractors = [title for title in pool if title != correct][:3]
        while len(distractors) < 3:
            distractors.append(self.fallback_option(level, category, len(distractors)))

        options = [(correct, True), *[(title, False) for title in distractors[:3]]]
        rotation = (level.order + order) % len(options)
        return options[rotation:] + options[:rotation]

    def fallback_option(self, level, category, index):
        category_name = category.name if category else "Geral"
        fallback_options = [
            f"Um texto de {level.name} sobre outro tema de {category_name}",
            f"Uma historia geral sem relacao direta com {category_name}",
            f"Uma pergunta de vocabulario fora desse trecho",
        ]
        return fallback_options[index % len(fallback_options)]
