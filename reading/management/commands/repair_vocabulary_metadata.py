from django.core.management.base import BaseCommand

from reading.content_pipeline import _translation_lookup, simplified_pronunciation, translation_for
from reading.models import VocabularyItem


class Command(BaseCommand):
    help = "Fill missing vocabulary translations and rewrite readable pronunciation hints."

    def handle(self, *args, **options):
        lookup = _translation_lookup()
        pending_values = {"", "Traducao pendente"}
        updated_items = []

        for item in VocabularyItem.objects.all().iterator(chunk_size=500):
            lemma = item.lemma_en or item.word_en
            translation = translation_for(lemma, lookup)
            pronunciation = simplified_pronunciation(item.word_en)

            changed = False
            if item.translation_pt in pending_values or item.translation_pt != translation:
                item.translation_pt = translation
                changed = True
            if item.pronunciation_pt != pronunciation:
                item.pronunciation_pt = pronunciation
                changed = True

            if changed:
                updated_items.append(item)

        if updated_items:
            VocabularyItem.objects.bulk_update(updated_items, ["translation_pt", "pronunciation_pt"], batch_size=500)

        remaining = VocabularyItem.objects.filter(translation_pt__iexact="Traducao pendente").count()
        self.stdout.write(
            self.style.SUCCESS(
                f"Vocabulary metadata repaired: {len(updated_items)} item(s) updated; pending translations: {remaining}."
            )
        )
