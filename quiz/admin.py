from django.contrib import admin

from .models import (
    PlacementQuizAnswer,
    PlacementQuizQuestion,
    QuizAttempt,
    TextQuizAnswer,
    TextQuizAttempt,
    TextQuizQuestion,
)


class PlacementQuizAnswerInline(admin.TabularInline):
    model = PlacementQuizAnswer
    extra = 4


@admin.register(PlacementQuizQuestion)
class PlacementQuizQuestionAdmin(admin.ModelAdmin):
    list_display = ("target_level", "category", "order", "is_active")
    list_filter = ("target_level", "category", "is_active")
    search_fields = ("question_text",)
    autocomplete_fields = ("target_level", "category")
    inlines = [PlacementQuizAnswerInline]


@admin.register(PlacementQuizAnswer)
class PlacementQuizAnswerAdmin(admin.ModelAdmin):
    list_display = ("answer_text", "question", "is_correct")
    list_filter = ("is_correct",)
    search_fields = ("answer_text", "question__question_text")


@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "target_level",
        "category",
        "score",
        "total_questions",
        "percentage",
        "recommended_level",
        "created_at",
    )
    list_filter = ("target_level", "category", "recommended_level")
    search_fields = ("user__username", "user__email")
    autocomplete_fields = ("user", "target_level", "category", "recommended_level")


class TextQuizAnswerInline(admin.TabularInline):
    model = TextQuizAnswer
    extra = 4


@admin.register(TextQuizQuestion)
class TextQuizQuestionAdmin(admin.ModelAdmin):
    list_display = ("text", "order", "is_active")
    list_filter = ("text__level", "text__category", "is_active")
    search_fields = ("question_text", "text__title")
    autocomplete_fields = ("text",)
    inlines = [TextQuizAnswerInline]


@admin.register(TextQuizAnswer)
class TextQuizAnswerAdmin(admin.ModelAdmin):
    list_display = ("answer_text", "question", "is_correct")
    list_filter = ("is_correct",)
    search_fields = ("answer_text", "question__question_text")


@admin.register(TextQuizAttempt)
class TextQuizAttemptAdmin(admin.ModelAdmin):
    list_display = ("user", "text", "score", "total_questions", "percentage", "coins_awarded", "created_at")
    list_filter = ("text__level", "text__category")
    search_fields = ("user__username", "user__email", "text__title")
    autocomplete_fields = ("user", "text")
