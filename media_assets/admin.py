from django.contrib import admin

from .models import VisualAsset


@admin.register(VisualAsset)
class VisualAssetAdmin(admin.ModelAdmin):
    list_display = ("title", "asset_type", "is_ai_generated", "created_at")
    list_filter = ("asset_type", "is_ai_generated")
    prepopulated_fields = {"slug": ("title",)}
    search_fields = ("title", "prompt", "attribution")
