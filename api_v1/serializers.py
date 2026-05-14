from rest_framework import serializers

from quiz.models import TextQuizAnswer, TextQuizQuestion
from reading.models import Text, VocabularyItem


class VocabularyItemSerializer(serializers.ModelSerializer):
    text_slug = serializers.CharField(source="text.slug", read_only=True)

    class Meta:
        model = VocabularyItem
        fields = [
            "id",
            "text",
            "text_slug",
            "word_en",
            "lemma_en",
            "part_of_speech",
            "translation_pt",
            "pronunciation_pt",
            "ipa",
            "audio_url",
            "tts_provider",
            "example_en",
            "source",
            "frequency_rank",
            "order",
        ]
        read_only_fields = ["id", "text_slug"]


class TextSerializer(serializers.ModelSerializer):
    level = serializers.CharField(source="level.slug", read_only=True)
    level_name = serializers.CharField(source="level.name", read_only=True)
    category = serializers.CharField(source="category.slug", read_only=True)
    category_name = serializers.CharField(source="category.name", read_only=True)
    character = serializers.CharField(source="character.slug", read_only=True, allow_null=True)
    absolute_url = serializers.CharField(source="get_absolute_url", read_only=True)
    vocabulary = VocabularyItemSerializer(many=True, read_only=True)

    class Meta:
        model = Text
        fields = [
            "id",
            "title",
            "slug",
            "summary_pt",
            "content_en",
            "level",
            "level_name",
            "category",
            "category_name",
            "character",
            "word_count",
            "estimated_reading_time",
            "image_prompt",
            "status",
            "published_at",
            "absolute_url",
            "vocabulary",
        ]
        read_only_fields = fields


class TextQuizAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = TextQuizAnswer
        fields = ["id", "answer_text", "is_correct"]
        read_only_fields = fields


class TextQuizQuestionSerializer(serializers.ModelSerializer):
    text_slug = serializers.CharField(source="text.slug", read_only=True)
    answers = TextQuizAnswerSerializer(many=True, read_only=True)

    class Meta:
        model = TextQuizQuestion
        fields = [
            "id",
            "text",
            "text_slug",
            "question_text",
            "order",
            "is_active",
            "answers",
        ]
        read_only_fields = fields
