from drf_spectacular.utils import OpenApiExample, extend_schema, inline_serializer
from rest_framework import serializers
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from quiz.models import TextQuizQuestion
from reading.models import Text, VocabularyItem
from services.ai_engine import explain_selection

from .serializers import TextQuizQuestionSerializer, TextSerializer, VocabularyItemSerializer


class TextListAPIView(generics.ListAPIView):
    serializer_class = TextSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        queryset = (
            Text.objects.filter(status="published")
            .select_related("level", "category", "character")
            .prefetch_related("vocabulary")
        )
        level = self.request.query_params.get("level")
        category = self.request.query_params.get("category")
        search = self.request.query_params.get("q")

        if level:
            queryset = queryset.filter(level__slug=level)
        if category:
            queryset = queryset.filter(category__slug=category)
        if search:
            queryset = queryset.filter(title__icontains=search)

        return queryset


class TextDetailAPIView(generics.RetrieveAPIView):
    serializer_class = TextSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = "slug"

    def get_queryset(self):
        return (
            Text.objects.filter(status="published")
            .select_related("level", "category", "character")
            .prefetch_related("vocabulary")
        )


class VocabularyItemListAPIView(generics.ListAPIView):
    serializer_class = VocabularyItemSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        queryset = VocabularyItem.objects.select_related("text", "text__level", "text__category")
        text_slug = self.request.query_params.get("text")
        if text_slug:
            queryset = queryset.filter(text__slug=text_slug)
        return queryset


class TextQuizListAPIView(generics.ListAPIView):
    serializer_class = TextQuizQuestionSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        queryset = (
            TextQuizQuestion.objects.filter(is_active=True, text__status="published")
            .select_related("text")
            .prefetch_related("answers")
            .order_by("text__slug", "order")
        )
        text_slug = self.request.query_params.get("text")
        if text_slug:
            queryset = queryset.filter(text__slug=text_slug)
        return queryset


class AIExplainAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        request=inline_serializer(
            name="AIExplainRequest",
            fields={
                "selection": serializers.CharField(),
                "context": serializers.CharField(required=False, allow_blank=True),
                "text_slug": serializers.CharField(required=False, allow_blank=True),
            },
        ),
        responses=inline_serializer(
            name="AIExplainResponse",
            fields={
                "selection": serializers.CharField(),
                "explanation_pt": serializers.CharField(),
                "key_words": serializers.ListField(child=serializers.DictField()),
                "grammar_note_pt": serializers.CharField(),
                "source": serializers.CharField(),
            },
        ),
        examples=[
            OpenApiExample(
                "Explicacao local",
                value={
                    "selection": "There is a tea on a small table.",
                    "text_slug": "warm-tea-in-tecnologia",
                },
                request_only=True,
            )
        ],
    )
    def post(self, request):
        selection = (request.data.get("selection") or request.data.get("text") or "").strip()
        context = (request.data.get("context") or "").strip()
        text_slug = (request.data.get("text_slug") or "").strip()

        if not selection:
            return Response(
                {"detail": "Envie um trecho no campo 'selection' ou 'text'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        glossary = {}
        if text_slug:
            glossary = {
                item.word_en.lower(): item.translation_pt
                for item in VocabularyItem.objects.filter(text__slug=text_slug).only("word_en", "translation_pt")
            }

        explanation = explain_selection(selection, context=context, glossary=glossary)
        return Response(explanation)
