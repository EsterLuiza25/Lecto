from django.contrib import admin

from .models import AvatarOption, UserAvatar, UserAvatarUnlock, UserProfile


@admin.register(AvatarOption)
class AvatarOptionAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "option_type",
        "coin_price",
        "required_category",
        "required_category_reads",
        "layer_order",
        "is_active",
    )
    list_filter = ("option_type", "required_category", "is_active")
    search_fields = ("name", "image_asset")
    autocomplete_fields = ("required_category",)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "display_name",
        "current_level",
        "coin_balance",
        "reading_streak",
        "longest_reading_streak",
        "last_read_at",
    )
    list_filter = ("current_level", "interests")
    search_fields = ("user__username", "user__email", "display_name")
    autocomplete_fields = ("user", "current_level", "avatar")
    filter_horizontal = ("interests",)


@admin.register(UserAvatar)
class UserAvatarAdmin(admin.ModelAdmin):
    list_display = ("user", "base_body", "body_style", "hair_style", "outfit", "eyes", "updated_at")
    search_fields = ("user__username", "user__email")
    autocomplete_fields = ("user", "base_body", "body_style", "hair_style", "outfit", "eyes")
    filter_horizontal = ("accessories",)


@admin.register(UserAvatarUnlock)
class UserAvatarUnlockAdmin(admin.ModelAdmin):
    list_display = ("user", "option", "coin_price_paid", "unlocked_at")
    list_filter = ("option__option_type",)
    search_fields = ("user__username", "user__email", "option__name")
    autocomplete_fields = ("user", "option")
