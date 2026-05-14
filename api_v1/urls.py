from django.urls import path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from . import views

app_name = "api_v1"

urlpatterns = [
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path("docs/", SpectacularSwaggerView.as_view(url_name="api_v1:schema"), name="swagger-ui"),
    path("texts/", views.TextListAPIView.as_view(), name="text-list"),
    path("texts/<slug:slug>/", views.TextDetailAPIView.as_view(), name="text-detail"),
    path("vocabulary/", views.VocabularyItemListAPIView.as_view(), name="vocabulary-list"),
    path("text-quizzes/", views.TextQuizListAPIView.as_view(), name="text-quiz-list"),
    path("ai/explain/", views.AIExplainAPIView.as_view(), name="ai-explain"),
]
