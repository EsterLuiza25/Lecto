from django.db import models


class VisualAsset(models.Model):
    ASSET_TYPE_CHOICES = [
        ("image", "Image"),
        ("animation", "Animation"),
        ("audio", "Audio"),
        ("other", "Other"),
    ]

    title = models.CharField(max_length=140)
    slug = models.SlugField(max_length=160, unique=True)
    asset_type = models.CharField(max_length=20, choices=ASSET_TYPE_CHOICES)
    file = models.FileField(upload_to="assets/", blank=True)
    external_url = models.URLField(blank=True)
    prompt = models.TextField(blank=True)
    attribution = models.CharField(max_length=200, blank=True)
    is_ai_generated = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title
