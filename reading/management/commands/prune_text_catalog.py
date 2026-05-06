from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from reading.models import Category, Level, Text


class Command(BaseCommand):
    help = "Keep only a fixed number of Text records per category and level, deleting extra records and their media files."

    def add_arguments(self, parser):
        parser.add_argument("--keep", type=int, default=10)
        parser.add_argument("--category", help="Optional category slug.")
        parser.add_argument("--level", help="Optional level slug.")
        parser.add_argument("--delete-media", action="store_true")
        parser.add_argument("--dry-run", action="store_true")

    def handle(self, *args, **options):
        keep = options["keep"]
        if keep < 1:
            raise CommandError("--keep must be at least 1.")

        categories = Category.objects.order_by("slug")
        levels = Level.objects.order_by("order")
        if options["category"]:
            categories = categories.filter(slug=options["category"])
        if options["level"]:
            levels = levels.filter(slug=options["level"])

        media_paths = []
        delete_ids = []
        kept_total = 0

        for category in categories:
            for level in levels:
                texts = list(
                    Text.objects.filter(category=category, level=level)
                    .order_by("id")
                    .only("id", "slug", "cover_image", "animation_asset")
                )
                keep_texts = texts[:keep]
                delete_texts = texts[keep:]
                kept_total += len(keep_texts)
                delete_ids.extend(text.id for text in delete_texts)
                for text in delete_texts:
                    media_paths.extend(self.media_paths_for(text))

                if delete_texts:
                    self.stdout.write(
                        f"{category.slug}/{level.slug}: keeping {len(keep_texts)}, deleting {len(delete_texts)}"
                    )

        self.stdout.write(f"Text records to keep: {kept_total}")
        self.stdout.write(f"Text records to delete: {len(delete_ids)}")
        self.stdout.write(f"Media files to delete: {len(media_paths)}")

        if options["dry_run"]:
            self.stdout.write(self.style.WARNING("Dry run only. No records or files were deleted."))
            return

        with transaction.atomic():
            Text.objects.filter(id__in=delete_ids).delete()

        deleted_files = 0
        if options["delete_media"]:
            for path in media_paths:
                if path.exists():
                    path.unlink()
                    deleted_files += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Pruned catalog: deleted {len(delete_ids)} texts and {deleted_files} media files."
            )
        )

    def media_paths_for(self, text):
        paths = []
        for field in (text.cover_image, text.animation_asset):
            if not field:
                continue
            paths.append(self.safe_media_path(field.name))
        return paths

    def safe_media_path(self, relative_name):
        media_root = Path(settings.MEDIA_ROOT).resolve()
        path = (media_root / relative_name).resolve()
        if media_root not in path.parents and path != media_root:
            raise CommandError(f"Refusing to delete file outside MEDIA_ROOT: {path}")
        return path
