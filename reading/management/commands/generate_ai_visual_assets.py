import base64
import json
import os
import time
import urllib.error
import urllib.request
from pathlib import Path

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand, CommandError
from django.utils.text import slugify

from accounts.models import AvatarOption
from reading.ai_asset_prompts import build_avatar_asset_prompt, build_text_image_prompt
from reading.models import Text


OPENAI_IMAGE_ENDPOINT = "https://api.openai.com/v1/images/generations"


class ImageGenerationError(RuntimeError):
    pass


class Command(BaseCommand):
    help = (
        "Generate technical image prompts for Text and AvatarOption records. "
        "Optionally call an image API, save files under media, and update cover_image/image_asset."
    )

    def add_arguments(self, parser):
        parser.add_argument("--texts", action="store_true", help="Process Text records.")
        parser.add_argument("--avatars", action="store_true", help="Process AvatarOption records.")
        parser.add_argument("--category", help="Limit texts by category slug.")
        parser.add_argument("--level", help="Limit texts by level slug.")
        parser.add_argument("--limit", type=int, help="Maximum number of texts to process.")
        parser.add_argument("--offset", type=int, default=0, help="Offset for text batching.")
        parser.add_argument("--only-missing-cover", action="store_true", help="Generate images only for texts without cover_image.")
        parser.add_argument("--avatar-type", help="Limit avatars by option_type, such as hair_style or outfit.")
        parser.add_argument("--provider", choices=["none", "openai"], default="none")
        parser.add_argument("--model", default="gpt-image-2")
        parser.add_argument("--size", default="1024x1024")
        parser.add_argument("--quality", default="medium")
        parser.add_argument("--force", action="store_true", help="Overwrite existing downloaded image files/fields.")
        parser.add_argument("--sleep", type=float, default=0.0, help="Seconds to wait between API calls.")
        parser.add_argument("--verbose", action="store_true")
        parser.add_argument("--dry-run", action="store_true")

    def handle(self, *args, **options):
        process_texts = options["texts"]
        process_avatars = options["avatars"]
        if not process_texts and not process_avatars:
            process_texts = True
            process_avatars = True

        client = None
        if options["provider"] == "openai":
            client = OpenAIImageClient(
                api_key=os.getenv("OPENAI_API_KEY", ""),
                model=options["model"],
                size=options["size"],
                quality=options["quality"],
            )

        text_count = 0
        avatar_count = 0
        generated_count = 0

        if process_texts:
            text_count, generated = self.process_texts(client, options)
            generated_count += generated

        if process_avatars:
            avatar_count, generated = self.process_avatars(client, options)
            generated_count += generated

        self.stdout.write(
            self.style.SUCCESS(
                f"AI asset pass complete: {text_count} text prompts, {avatar_count} avatar prompts, "
                f"{generated_count} generated files."
            )
        )

    def process_texts(self, client, options):
        texts = Text.objects.select_related("level", "category", "character").order_by("id")
        if options["category"]:
            texts = texts.filter(category__slug=options["category"])
        if options["level"]:
            texts = texts.filter(level__slug=options["level"])
        if options["offset"]:
            texts = texts[options["offset"] :]
        if options["limit"]:
            texts = texts[: options["limit"]]

        prompt_count = 0
        generated_count = 0
        for text in texts:
            prompt = build_text_image_prompt(text)
            prompt_changed = text.image_prompt != prompt

            if not options["dry_run"] and prompt_changed:
                text.image_prompt = prompt
                text.save(update_fields=["image_prompt", "updated_at"])
            prompt_count += 1

            should_generate = bool(client)
            if options["only_missing_cover"] and text.cover_image and not options["force"]:
                should_generate = False
            if text.cover_image and not options["force"]:
                should_generate = False

            if should_generate:
                image_bytes = client.generate(prompt)
                file_name = f"{text.slug}.png"
                if not options["dry_run"]:
                    text.cover_image.save(file_name, ContentFile(image_bytes), save=True)
                generated_count += 1
                self.stdout.write(f"Generated cover: {text.slug}")
                self.sleep(options)
            elif prompt_changed and options["verbose"]:
                self.stdout.write(f"Prompt updated: {text.slug}")

        return prompt_count, generated_count

    def process_avatars(self, client, options):
        options_qs = AvatarOption.objects.filter(is_active=True).exclude(option_type="preset").order_by(
            "option_type",
            "layer_order",
            "name",
        )
        if options["avatar_type"]:
            options_qs = options_qs.filter(option_type=options["avatar_type"])

        manifest = []
        generated_count = 0
        for option in options_qs:
            prompt = build_avatar_asset_prompt(option)
            file_name = self.avatar_file_name(option)
            manifest.append(
                {
                    "id": option.id,
                    "name": option.name,
                    "option_type": option.option_type,
                    "coin_price": option.coin_price,
                    "layer_order": option.layer_order,
                    "current_asset": option.image_asset.name if option.image_asset else "",
                    "generated_asset": f"avatars/{file_name}",
                    "prompt": prompt,
                }
            )

            should_generate = bool(client)
            if option.image_asset and not options["force"]:
                should_generate = False

            if should_generate:
                image_bytes = client.generate(prompt, transparent=True)
                if not options["dry_run"]:
                    option.image_asset.save(file_name, ContentFile(image_bytes), save=True)
                generated_count += 1
                self.stdout.write(f"Generated avatar layer: {option.name}")
                self.sleep(options)

        if not options["dry_run"]:
            self.write_avatar_manifest(manifest)
        self.stdout.write(f"Avatar prompt manifest entries: {len(manifest)}")
        return len(manifest), generated_count

    def write_avatar_manifest(self, manifest):
        manifest_dir = Path(settings.MEDIA_ROOT) / "avatars" / "generated"
        manifest_dir.mkdir(parents=True, exist_ok=True)
        manifest_path = manifest_dir / "avatar_asset_prompts.json"
        manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")

    def avatar_file_name(self, option):
        slug = slugify(f"{option.option_type}-{option.name}") or f"avatar-option-{option.id}"
        return f"generated/{option.option_type}/{slug}.png"

    def sleep(self, options):
        if options["sleep"] > 0:
            time.sleep(options["sleep"])


class OpenAIImageClient:
    def __init__(self, api_key, model, size, quality):
        if not api_key:
            raise CommandError("OPENAI_API_KEY is required when --provider=openai.")
        self.api_key = api_key
        self.model = model
        self.size = size
        self.quality = quality

    def generate(self, prompt, transparent=False):
        payload = {
            "model": self.model,
            "prompt": prompt,
            "size": self.size,
            "quality": self.quality,
            "n": 1,
        }
        if transparent:
            payload["background"] = "transparent"
            payload["output_format"] = "png"

        request = urllib.request.Request(
            OPENAI_IMAGE_ENDPOINT,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(request, timeout=180) as response:
                body = response.read().decode("utf-8")
        except urllib.error.HTTPError as error:
            detail = error.read().decode("utf-8", errors="replace")
            raise ImageGenerationError(f"OpenAI image request failed: {error.code} {detail}") from error
        except urllib.error.URLError as error:
            raise ImageGenerationError(f"OpenAI image request failed: {error}") from error

        data = json.loads(body)
        item = (data.get("data") or [{}])[0]
        if item.get("b64_json"):
            return base64.b64decode(item["b64_json"])
        if item.get("url"):
            return self.download(item["url"])
        raise ImageGenerationError("OpenAI image response did not include b64_json or url.")

    def download(self, url):
        request = urllib.request.Request(url, headers={"User-Agent": "LectoAssetGenerator/1.0"})
        with urllib.request.urlopen(request, timeout=180) as response:
            return response.read()
