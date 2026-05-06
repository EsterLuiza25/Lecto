from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST

from accounts.models import AvatarOption, UserProfile
from progress.services import category_reading_stats, completed_read_count
from reading.models import Category, Level, Text


def home(request):
    levels = Level.objects.all()
    categories = Category.objects.filter(is_active=True)[:12]
    featured_texts = (
        Text.objects.filter(status="published")
        .select_related("level", "category")
        .defer("content_en", "image_prompt")
        [:6]
    )

    return render(
        request,
        "core/home.html",
        {
            "levels": levels,
            "categories": categories,
            "featured_texts": featured_texts,
        },
    )


def avatar(request):
    layer_labels = {
        "base_body": "Corpo base",
        "body_style": "Masculino / Feminino",
        "hair_style": "Cabelo",
        "outfit": "Roupa",
        "eyes": "Olhos",
        "accessory": "Acessorios",
    }
    layer_order = ["base_body", "body_style", "hair_style", "outfit", "eyes", "accessory"]
    options_by_type = {
        option_type: list(
            AvatarOption.objects.filter(option_type=option_type, is_active=True)
            .select_related("required_category")
            .order_by(
                "layer_order",
                "coin_price",
                "name",
            )
        )
        for option_type in layer_order
    }

    profile = None
    total_completed_reads = 0
    category_stats = []
    if request.user.is_authenticated:
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        total_completed_reads = completed_read_count(request.user)
        category_stats = category_reading_stats(request.user)
        for options in options_by_type.values():
            for option in options:
                option.unlock_state = option.unlock_status_for(request.user)
    else:
        for options in options_by_type.values():
            for option in options:
                option.unlock_state = option.unlock_status_for(None)

    avatar_layers = [
        {
            "type": option_type,
            "label": layer_labels[option_type],
            "options": options_by_type[option_type],
        }
        for option_type in layer_order
    ]

    return render(
        request,
        "core/avatar.html",
        {
            "avatar_layers": avatar_layers,
            "profile": profile,
            "total_completed_reads": total_completed_reads,
            "category_stats": category_stats,
        },
    )


@login_required
@require_POST
def purchase_avatar_option(request, option_id):
    option = get_object_or_404(AvatarOption.objects.select_related("required_category"), id=option_id, is_active=True)
    try:
        unlock = option.unlock_for(request.user)
    except ValidationError as error:
        return JsonResponse({"ok": False, "error": "; ".join(error.messages)}, status=400)

    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    return JsonResponse(
        {
            "ok": True,
            "option_id": option.id,
            "unlocked_at": unlock.unlocked_at.isoformat(),
            "coin_balance": profile.coin_balance,
        }
    )
