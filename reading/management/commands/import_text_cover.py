from pathlib import Path

from django.core.files import File
from django.core.management.base import BaseCommand, CommandError

from reading.models import Text


class Command(BaseCommand):
    help = "Attach a local image file to a Text.cover_image field by text slug."

    def add_arguments(self, parser):
        parser.add_argument("slug")
        parser.add_argument("image_path")
        parser.add_argument("--force", action="store_true")

    def handle(self, *args, **options):
        text = Text.objects.get(slug=options["slug"])
        image_path = Path(options["image_path"]).expanduser().resolve()
        if not image_path.exists() or not image_path.is_file():
            raise CommandError(f"Image file not found: {image_path}")

        if text.cover_image and not options["force"]:
            raise CommandError(
                f"{text.slug} already has cover_image={text.cover_image.name}. Use --force to replace it."
            )

        extension = image_path.suffix.lower() or ".png"
        file_name = f"{text.slug}{extension}"
        with image_path.open("rb") as image_file:
            text.cover_image.save(file_name, File(image_file), save=True)

        self.stdout.write(
            self.style.SUCCESS(
                f"Updated {text.slug}: cover_image={text.cover_image.name}; "
                f"animation_asset kept as {text.animation_asset.name or 'empty'}."
            )
        )
