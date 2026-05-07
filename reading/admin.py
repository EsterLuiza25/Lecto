from django.contrib import admin

from .models import Category, Character, Level, Text, VocabularyItem


@admin.register(Level)
class LevelAdmin(admin.ModelAdmin):
    list_display = ("name", "order", "min_words", "max_words")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "is_active")
    list_filter = ("is_active",)
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name", "description_pt")


@admin.register(Character)
class CharacterAdmin(admin.ModelAdmin):
    list_display = ("name", "publisher", "is_active")
    list_filter = ("publisher", "is_active")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name", "description_pt")


class VocabularyItemInline(admin.TabularInline):
    model = VocabularyItem
    extra = 1


@admin.register(Text)
class TextAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "level",
        "category",
        "status",
        "word_count",
        "estimated_reading_time",
        "is_premium",
        "published_at",
    )
    list_filter = ("status", "level", "category", "is_premium")
    prepopulated_fields = {"slug": ("title",)}
    search_fields = ("title", "summary_pt", "content_en")
    autocomplete_fields = ("level", "category", "character")
    inlines = [VocabularyItemInline]


@admin.register(VocabularyItem)
class VocabularyItemAdmin(admin.ModelAdmin):
    list_display = ("word_en", "part_of_speech", "source", "frequency_rank", "translation_pt", "text", "order")
    list_filter = ("source", "part_of_speech", "text__level", "text__category")
    search_fields = ("word_en", "lemma_en", "translation_pt", "example_en", "text__title")
