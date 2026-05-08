from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from progress.models import FavoriteText, ReadingProgress
from progress.services import process_completed_reading

from .artwork import build_text_illustration_svg
from .models import Category, Character, Level, Text


def _published_texts():
    return Text.objects.filter(status="published").select_related("level", "category", "character")


def _published_text_cards():
    return _published_texts().defer("content_en", "image_prompt")


def level_list(request):
    return render(request, "reading/level_list.html", {"levels": Level.objects.all()})


def level_detail(request, slug):
    level = get_object_or_404(Level, slug=slug)
    texts = _published_text_cards().filter(level=level)
    category_slug = request.GET.get("categoria")
    query = request.GET.get("q", "")

    if category_slug:
        texts = texts.filter(category__slug=category_slug)

    if query:
        texts = texts.filter(
            Q(title__icontains=query)
            | Q(summary_pt__icontains=query)
            | Q(content_en__icontains=query)
            | Q(category__name__icontains=query)
        )

    paginator = Paginator(texts, 24)
    page_obj = paginator.get_page(request.GET.get("page"))
    query_params = request.GET.copy()
    query_params.pop("page", None)

    return render(
        request,
        "reading/level_detail.html",
        {
            "level": level,
            "texts": page_obj,
            "page_obj": page_obj,
            "extra_query": query_params.urlencode(),
            "categories": Category.objects.filter(is_active=True),
            "selected_category": category_slug,
            "query": query,
        },
    )


def category_list(request):
    categories = Category.objects.filter(is_active=True)
    return render(request, "reading/category_list.html", {"categories": categories})


def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug, is_active=True)
    texts = _published_text_cards().filter(category=category)
    level_slug = request.GET.get("nivel")
    character_slug = request.GET.get("personagem")

    if level_slug:
        texts = texts.filter(level__slug=level_slug)

    if character_slug and category.slug == "hqs":
        texts = texts.filter(character__slug=character_slug)

    paginator = Paginator(texts, 24)
    page_obj = paginator.get_page(request.GET.get("page"))
    query_params = request.GET.copy()
    query_params.pop("page", None)
    characters = Character.objects.filter(is_active=True, texts__category=category).distinct()

    return render(
        request,
        "reading/category_detail.html",
        {
            "category": category,
            "texts": page_obj,
            "page_obj": page_obj,
            "extra_query": query_params.urlencode(),
            "levels": Level.objects.all(),
            "selected_level": level_slug,
            "characters": characters,
            "selected_character": character_slug,
        },
    )


def text_detail(request, slug):
    text = get_object_or_404(_published_texts().prefetch_related("vocabulary"), slug=slug)
    progress = None
    is_favorited = False

    if request.user.is_authenticated:
        progress, _ = ReadingProgress.objects.get_or_create(user=request.user, text=text)
        is_favorited = FavoriteText.objects.filter(user=request.user, text=text).exists()

    return render(
        request,
        "reading/text_detail.html",
        {
            "text": text,
            "progress": progress,
            "is_favorited": is_favorited,
        },
    )


def text_artwork(request, slug):
    text = get_object_or_404(_published_texts(), slug=slug)
    svg = build_text_illustration_svg(text)
    response = HttpResponse(svg, content_type="image/svg+xml")
    response["Cache-Control"] = "public, max-age=86400"
    return response


@login_required
def toggle_favorite(request, slug):
    text = get_object_or_404(_published_texts(), slug=slug)
    favorite, created = FavoriteText.objects.get_or_create(user=request.user, text=text)

    if not created:
        favorite.delete()

    return redirect(text.get_absolute_url())


@login_required
def mark_completed(request, slug):
    text = get_object_or_404(_published_texts(), slug=slug)
    process_completed_reading(request.user, text)

    return redirect(text.get_absolute_url())
