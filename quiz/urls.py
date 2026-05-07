from django.urls import path
from django.views.generic import RedirectView

from . import views

app_name = "quiz"

urlpatterns = [
    path("", RedirectView.as_view(pattern_name="quiz:placement_start", permanent=False), name="quiz_home"),
    path("nivelamento/", views.placement_start, name="placement_start"),
    path("texto/<slug:slug>/", views.text_quiz, name="text_quiz"),
]
