from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from reading.artwork import write_text_illustration
from reading.models import Text


class Command(BaseCommand):
    help = "Replace old generated assets with static themed SVG illustrations for every published text."

    def add_arguments(self, parser):
        parser.add_argument("--delete-old-animations", action="store_true")
        parser.add_argument("--batch-size", type=int, default=300)

    def handle(self, *args, **options):
        batch_size = options["batch_size"]
        queryset = (
            Text.objects.filter(status="published")
            .select_related("level", "category")
            .order_by("level__order", "category__slug", "slug")
        )

        total = queryset.count()
        self.stdout.write(f"Refreshing themed illustrations for {total} texts...")

        updated = 0
        pending = []
        for text in queryset.iterator(chunk_size=batch_size):
            illustration_path = write_text_illustration(text)
            if text.animation_asset.name != illustration_path:
                text.animation_asset = illustration_path
                pending.append(text)

            if len(pending) >= batch_size:
                updated += self.flush_updates(pending)
                pending = []
                self.stdout.write(f"{updated} database references updated...")

        updated += self.flush_updates(pending)

        if options["delete_old_animations"]:
            removed = self.delete_old_animations()
            self.stdout.write(self.style.WARNING(f"Old SVG files removed: {removed}"))

        self.stdout.write(self.style.SUCCESS(f"Illustrations ready. References updated: {updated}."))

    def flush_updates(self, texts):
        if not texts:
            return 0
        Text.objects.bulk_update(texts, ["animation_asset"])
        return len(texts)

    def delete_old_animations(self):
        media_root = Path(settings.MEDIA_ROOT).resolve()
        animation_dir = (media_root / "texts" / "animations").resolve()

        if not animation_dir.exists():
            return 0

        if media_root not in animation_dir.parents:
            raise RuntimeError(f"Refusing to delete files outside MEDIA_ROOT: {animation_dir}")

        removed = 0
        for path in animation_dir.glob("*.svg"):
            if animation_dir not in path.resolve().parents:
                continue
            path.unlink()
            removed += 1
        return removed
