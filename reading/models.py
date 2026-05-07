from django.db import models
from django.urls import reverse


class Level(models.Model):
    name = models.CharField(max_length=40, unique=True)
    slug = models.SlugField(max_length=40, unique=True)
    order = models.PositiveSmallIntegerField(unique=True)
    description_pt = models.TextField(blank=True)
    min_words = models.PositiveSmallIntegerField(default=40)
    max_words = models.PositiveSmallIntegerField(default=80)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(max_length=90, unique=True)
    description_pt = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name


class Character(models.Model):
    PUBLISHER_CHOICES = [
        ("marvel", "Marvel"),
        ("dc", "DC"),
        ("other", "Other"),
    ]

    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(max_length=90, unique=True)
    publisher = models.CharField(max_length=20, choices=PUBLISHER_CHOICES)
    description_pt = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Text(models.Model):
    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("published", "Published"),
        ("archived", "Archived"),
    ]

    title = models.CharField(max_length=180)
    slug = models.SlugField(max_length=200, unique=True)
    summary_pt = models.TextField()
    content_en = models.TextField()
    level = models.ForeignKey(Level, on_delete=models.PROTECT, related_name="texts")
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="texts")
    character = models.ForeignKey(
        Character,
        on_delete=models.SET_NULL,
        related_name="texts",
        blank=True,
        null=True,
    )
    cover_image = models.FileField(upload_to="texts/covers/", blank=True)
    animation_asset = models.FileField(upload_to="texts/animations/", blank=True)
    image_prompt = models.TextField(blank=True)
    image_canvas_width = models.PositiveSmallIntegerField(default=500)
    image_canvas_height = models.PositiveSmallIntegerField(default=500)
    word_count = models.PositiveIntegerField(default=0)
    estimated_reading_time = models.PositiveSmallIntegerField(default=1)
    is_premium = models.BooleanField(default=False)
    view_count = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")
    published_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-published_at", "-created_at"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("reading:text_detail", kwargs={"slug": self.slug})


class VocabularyItem(models.Model):
    PART_OF_SPEECH_CHOICES = [
        ("noun", "Noun"),
        ("verb", "Verb"),
        ("adjective", "Adjective"),
    ]

    SOURCE_CHOICES = [
        ("manual", "Manual"),
        ("dynamic_nlp", "Dynamic NLP"),
        ("imported", "Imported"),
    ]

    text = models.ForeignKey(Text, on_delete=models.CASCADE, related_name="vocabulary")
    word_en = models.CharField(max_length=80)
    lemma_en = models.CharField(max_length=80, blank=True)
    part_of_speech = models.CharField(max_length=20, choices=PART_OF_SPEECH_CHOICES, blank=True)
    translation_pt = models.CharField(max_length=160)
    pronunciation_pt = models.CharField(max_length=120)
    ipa = models.CharField(max_length=120, blank=True)
    audio_url = models.URLField(blank=True)
    tts_provider = models.CharField(max_length=80, blank=True)
    example_en = models.CharField(max_length=240, blank=True)
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default="manual")
    frequency_rank = models.PositiveIntegerField(blank=True, null=True)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order", "word_en"]
        unique_together = ["text", "word_en"]
        indexes = [
            models.Index(fields=["part_of_speech", "source"]),
            models.Index(fields=["lemma_en"]),
        ]

    def __str__(self):
        return f"{self.word_en} ({self.text.title})"
