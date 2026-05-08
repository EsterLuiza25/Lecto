from decimal import Decimal

from django.shortcuts import get_object_or_404, render

from reading.models import Category, Level, Text
from .models import (
    PlacementQuizQuestion,
    QuizAttempt,
    TextQuizAttempt,
)


LEVEL_FIELD_NAME = "nivel"
CATEGORY_FIELD_NAME = "categoria"
MODE_FIELD_NAME = "modo"
DIAGNOSTIC_MODE = "diagnostico"


def placement_start(request):
    levels = list(Level.objects.all())
    categories = Category.objects.filter(is_active=True)
    selected_level = None
    selected_category = None
    questions = []
    result = None

    request_data = request.POST if request.method == "POST" else request.GET
    level_slug = request_data.get(LEVEL_FIELD_NAME, "").strip()
    category_slug = request_data.get(CATEGORY_FIELD_NAME, "").strip()
    quiz_mode = request_data.get(MODE_FIELD_NAME, "").strip()
    is_diagnostic = quiz_mode == DIAGNOSTIC_MODE

    if is_diagnostic:
        questions = diagnostic_questions(levels)
    elif level_slug:
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

        questions = list(
            PlacementQuizQuestion.objects.filter(**question_filters)
            .prefetch_related("answers")
            .order_by("order")[:7]
        )

    if request.method == "POST" and questions and (selected_level or is_diagnostic):
        total = len(questions)
        score_by_level = {}
        total_by_level = {}
        question_results = build_answer_feedback(questions, request.POST)
        score = sum(1 for row in question_results if row["is_correct"])

        for row in question_results:
            question = row["question"]
            total_by_level[question.target_level_id] = total_by_level.get(question.target_level_id, 0) + 1
            if row["is_correct"]:
                score_by_level[question.target_level_id] = score_by_level.get(question.target_level_id, 0) + 1

        percentage = Decimal(score * 100) / Decimal(total or 1)
        passed = score >= 5
        if is_diagnostic:
            recommended_level = diagnostic_recommended_level(levels, score)
            target_level = recommended_level
        else:
            recommended_level = selected_level if passed else previous_level(selected_level)
            target_level = selected_level

        if request.user.is_authenticated:
            user = request.user
        else:
            user = None

        QuizAttempt.objects.create(
            user=user,
            target_level=target_level,
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
            "is_diagnostic": is_diagnostic,
            "level_breakdown": diagnostic_level_breakdown(levels, score_by_level, total_by_level)
            if is_diagnostic
            else [],
            "question_results": question_results,
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
            "is_diagnostic": is_diagnostic,
            "diagnostic_mode": DIAGNOSTIC_MODE,
        },
    )


def text_quiz(request, slug):
    text = get_object_or_404(
        Text.objects.filter(status="published").prefetch_related("quiz_questions__answers"),
        slug=slug,
    )
    questions = list(text.quiz_questions.filter(is_active=True).prefetch_related("answers").order_by("order")[:5])
    result = None

    if request.method == "POST":
        total = len(questions)
        question_results = build_answer_feedback(questions, request.POST)
        score = sum(1 for row in question_results if row["is_correct"])

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
            "question_results": question_results,
        }

    return render(request, "quiz/text_quiz.html", {"text": text, "questions": questions, "result": result})


def previous_level(level):
    return Level.objects.filter(order__lt=level.order).order_by("-order").first() or level


def diagnostic_questions(levels):
    questions = []
    for level in levels:
        question = (
            PlacementQuizQuestion.objects.filter(
                target_level=level,
                category__isnull=True,
                is_active=True,
            )
            .prefetch_related("answers")
            .order_by("order")
            .first()
        )
        if question:
            questions.append(question)
    return questions


def diagnostic_recommended_level(levels, score):
    if not levels:
        return None
    if score <= 1:
        return levels[0]
    level_index = min(score - 1, len(levels) - 1)
    return levels[level_index]


def diagnostic_level_breakdown(levels, score_by_level, total_by_level):
    rows = []
    for level in levels:
        total = total_by_level.get(level.id, 0)
        if not total:
            continue
        score = score_by_level.get(level.id, 0)
        rows.append(
            {
                "level": level,
                "score": score,
                "total": total,
            }
        )
    return rows


def build_answer_feedback(questions, request_data):
    rows = []
    for question in questions:
        selected_answer = None
        correct_answer = None
        selected_id = request_data.get(f"question_{question.id}")

        for answer in question.answers.all():
            if str(answer.id) == str(selected_id):
                selected_answer = answer
            if answer.is_correct:
                correct_answer = answer

        rows.append(
            {
                "question": question,
                "selected_answer": selected_answer,
                "correct_answer": correct_answer,
                "is_correct": bool(selected_answer and selected_answer.is_correct),
            }
        )
    return rows
