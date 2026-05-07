from django.contrib import admin

from .models import Achievement, CoinTransaction, FavoriteText, ReadingProgress, UserAchievement


@admin.register(ReadingProgress)
class ReadingProgressAdmin(admin.ModelAdmin):
    list_display = ("user", "text", "status", "coins_awarded", "started_at", "completed_at")
    list_filter = ("status", "text__level", "text__category")
    search_fields = ("user__username", "user__email", "text__title")
    autocomplete_fields = ("user", "text")


@admin.register(FavoriteText)
class FavoriteTextAdmin(admin.ModelAdmin):
    list_display = ("user", "text", "created_at")
    list_filter = ("text__level", "text__category")
    search_fields = ("user__username", "user__email", "text__title")
    autocomplete_fields = ("user", "text")


@admin.register(CoinTransaction)
class CoinTransactionAdmin(admin.ModelAdmin):
    list_display = ("user", "amount", "reason", "related_text", "created_at")
    list_filter = ("reason",)
    search_fields = ("user__username", "user__email", "related_text__title")
    autocomplete_fields = ("user", "related_text", "related_quiz_attempt")


@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ("name", "coin_reward", "is_active")
    list_filter = ("is_active",)
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name", "description_pt")


@admin.register(UserAchievement)
class UserAchievementAdmin(admin.ModelAdmin):
    list_display = ("user", "achievement", "earned_at")
    search_fields = ("user__username", "user__email", "achievement__name")
    autocomplete_fields = ("user", "achievement")
