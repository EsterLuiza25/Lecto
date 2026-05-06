from decimal import Decimal

from django.shortcuts import get_object_or_404, render

from reading.models import Category, Level, Text
from .models import (
    PlacementQuizAnswer,
    PlacementQuizQuestion,
    QuizAttempt,
    TextQuizAnswer,
    TextQuizAttempt,
)


LEVEL_FIELD_NAME = "nivel"
CATEGORY_FIELD_NAME = "categoria"


def placement_start(request):
    levels = Level.objects.all()
    categories = Category.objects.filter(is_active=True)
    selected_level = None
    selected_category = None
    questions = PlacementQuizQuestion.objects.none()
    result = None

    request_data = request.POST if request.method == "POST" else request.GET
    level_slug = request_data.get(LEVEL_FIELD_NAME, "").strip()
    category_slug = request_data.get(CATEGORY_FIELD_NAME, "").strip()

    if level_slug:
        selected_level = get_object_or_404(Level, slug=level_slug)
        question_filters = {
            "target_level": selected_level,
            "is_active": True,
        }

        if category_slug:
            selected_category = get_object_or_404(Category, slug=category_slug, is_active=True)
            question_filters["category"] = selected_category
        else:
            question_filters["category__isnull"] = True

        questions = (
            PlacementQuizQuestion.objects.filter(**question_filters)
            .prefetch_related("answers")
            .order_by("order")[:7]
        )

    if request.method == "POST" and selected_level and questions.exists():
        score = 0
        total = questions.count()

        for question in questions:
            answer_id = request.POST.get(f"question_{question.id}")
            if answer_id and PlacementQuizAnswer.objects.filter(
                id=answer_id,
                question=question,
                is_correct=True,
            ).exists():
                score += 1

        percentage = Decimal(score * 100) / Decimal(total or 1)
        passed = score >= 5
        recommended_level = selected_level if passed else previous_level(selected_level)

        if request.user.is_authenticated:
            user = request.user
        else:
            user = None

        QuizAttempt.objects.create(
            user=user,
            target_level=selected_level,
            category=selected_category,
            score=score,
            total_questions=total,
            percentage=percentage,
            recommended_level=recommended_level,
        )

        result = {
            "score": score,
            "errors": total - score,
            "total": total,
            "percentage": percentage,
            "passed": passed,
            "recommended_level": recommended_level,
        }

    return render(
        request,
        "quiz/placement_start.html",
        {
            "levels": levels,
            "categories": categories,
            "selected_level": selected_level,
            "selected_category": selected_category,
            "questions": questions,
            "result": result,
        },
    )


def text_quiz(request, slug):
    text = get_object_or_404(
        Text.objects.filter(status="published").prefetch_related("quiz_questions__answers"),
        slug=slug,
    )
    questions = text.quiz_questions.filter(is_active=True).prefetch_related("answers").order_by("order")[:5]
    result = None

    if request.method == "POST":
        score = 0
        total = questions.count()

        for question in questions:
            answer_id = request.POST.get(f"question_{question.id}")
            if answer_id and TextQuizAnswer.objects.filter(
                id=answer_id,
                question=question,
                is_correct=True,
            ).exists():
                score += 1

        percentage = Decimal(score * 100) / Decimal(total or 1)
        coins_awarded = score
        if score >= 4:
            coins_awarded += 5

        if request.user.is_authenticated:
            TextQuizAttempt.objects.create(
                user=request.user,
                text=text,
                score=score,
                total_questions=total,
                percentage=percentage,
                coins_awarded=coins_awarded,
            )

        result = {
            "score": score,
            "errors": total - score,
            "total": total,
            "percentage": percentage,
            "coins_awarded": coins_awarded,
        }

    return render(request, "quiz/text_quiz.html", {"text": text, "questions": questions, "result": result})


def previous_level(level):
    return Level.objects.filter(order__lt=level.order).order_by("-order").first() or level
