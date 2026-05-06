from django.urls import path
from django.views.generic import RedirectView

from . import views

app_name = "reading"

urlpatterns = [
    path("", RedirectView.as_view(pattern_name="reading:level_list", permanent=False), name="reading_home"),
    path("niveis/", views.level_list, name="level_list"),
    path("nivel/<slug:slug>/", views.level_detail, name="level_detail"),
    path("categorias/", views.category_list, name="category_list"),
    path("categoria/<slug:slug>/", views.category_detail, name="category_detail"),
    path("texto/<slug:slug>/", views.text_detail, name="text_detail"),
    path("texto/<slug:slug>/favorito/", views.toggle_favorite, name="toggle_favorite"),
    path("texto/<slug:slug>/concluir/", views.mark_completed, name="mark_completed"),
]
