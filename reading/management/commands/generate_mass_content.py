from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from accounts.models import AvatarOption
from reading.avatar_art import build_cartoon_avatar_svg
from reading.artwork import write_text_illustration
from reading.content_pipeline import (
    LEVEL_WORD_LIMITS,
    build_image_prompt,
    enforce_level_word_limits,
    load_frequency_words,
    replace_text_vocabulary,
    word_count,
)
from reading.models import Category, Text


AVATAR_LAYER_OPTIONS = [
    ("Base clara", "base_body", "avatars/base/base-clara.svg", 0, 10),
    ("Base media", "base_body", "avatars/base/base-media.svg", 0, 10),
    ("Base escura", "base_body", "avatars/base/base-escura.svg", 0, 10),
    ("Base quente", "base_body", "avatars/base/base-quente.svg", 0, 10),
    ("Base dourada Lecto", "base_body", "avatars/base/base-dourada-lecto.svg", 60, 10),
    ("Masculino", "body_style", "avatars/body/masculino.svg", 0, 20),
    ("Feminino", "body_style", "avatars/body/feminino.svg", 0, 20),
    ("Cabelo azul curto", "hair_style", "avatars/hair/azul-curto.svg", 0, 30),
    ("Cabelo turquesa", "hair_style", "avatars/hair/turquesa.svg", 0, 30),
    ("Cabelo laranja longo", "hair_style", "avatars/hair/laranja-longo.svg", 0, 30),
    ("Cabelo cacheado", "hair_style", "avatars/hair/cacheado.svg", 0, 30),
    ("Cabelo preto longo", "hair_style", "avatars/hair/preto-longo.svg", 0, 30),
    ("Cabelo castanho curto", "hair_style", "avatars/hair/castanho-curto.svg", 0, 30),
    ("Careca estiloso", "hair_style", "avatars/hair/careca-estiloso.svg", 0, 30),
    ("Lenco violeta", "hair_style", "avatars/hair/lenco-violeta.svg", 80, 30),
    ("Olhos curiosos", "eyes", "avatars/eyes/curiosos.svg", 0, 40),
    ("Olhos felizes", "eyes", "avatars/eyes/felizes.svg", 0, 40),
    ("Olhos focados", "eyes", "avatars/eyes/focados.svg", 0, 40),
    ("Olhos serenos", "eyes", "avatars/eyes/serenos.svg", 0, 40),
    ("Piscadinha", "eyes", "avatars/eyes/piscadinha.svg", 0, 40),
    ("Blusa Lecto", "outfit", "avatars/outfits/blusa-lecto.svg", 0, 50),
    ("Casaco coral", "outfit", "avatars/outfits/casaco-coral.svg", 0, 50),
    ("Moletom violeta", "outfit", "avatars/outfits/moletom-violeta.svg", 0, 50),
    ("Camisa turquesa", "outfit", "avatars/outfits/camisa-turquesa.svg", 0, 50),
    ("Jaqueta academica", "outfit", "avatars/outfits/jaqueta-academica.svg", 0, 50),
    ("Sueter dourado", "outfit", "avatars/outfits/sueter-dourado.svg", 0, 50),
    ("Cachecol dourado", "outfit", "avatars/outfits/cachecol-dourado.svg", 90, 50),
    ("Oculos redondo", "accessory", "avatars/accessories/oculos-redondo.svg", 0, 70),
    ("Fones azul", "accessory", "avatars/accessories/fones-azul.svg", 0, 70),
    ("Brinco dourado", "accessory", "avatars/accessories/brinco-dourado.svg", 0, 70),
    ("Gravata borboleta", "accessory", "avatars/accessories/gravata-borboleta.svg", 0, 70),
    ("Gorro academico", "accessory", "avatars/accessories/gorro-academico.svg", 85, 70),
    ("Livro lateral", "accessory", "avatars/accessories/livro-lateral.svg", 95, 70),
]

AVATAR_CATEGORY_REQUIREMENTS = {
    "Base dourada Lecto": ("cotidiano", 10),
    "Lenco violeta": ("cultura-pop", 10),
    "Cachecol dourado": ("viagens", 10),
    "Fones azul": ("tecnologia", 10),
    "Gorro academico": ("cotidiano", 10),
    "Livro lateral": ("contos", 10),
}


class Command(BaseCommand):
    help = "Regenerate NLP vocabulary, image prompts/assets, word-count metadata, and avatar layer options in bulk."

    def add_arguments(self, parser):
        parser.add_argument("--limit", type=int, default=0)
        parser.add_argument("--frequency-list", default="", help="Path to a newline-based high-frequency word list.")
        parser.add_argument("--max-vocab", type=int, default=8)
        parser.add_argument("--skip-vocabulary", action="store_true")
        parser.add_argument("--skip-prompts", action="store_true")
        parser.add_argument("--skip-images", action="store_true")
        parser.add_argument("--skip-avatars", action="store_true")
        parser.add_argument("--only-avatars", action="store_true")
        parser.add_argument("--repair-stories", action="store_true")
        parser.add_argument("--warning-limit", type=int, default=20)
        parser.add_argument("--dry-run", action="store_true")

    def handle(self, *args, **options):
        frequency_words = load_frequency_words(options["frequency_list"] or None)

        if not options["skip_avatars"]:
            self.seed_avatar_layers(dry_run=options["dry_run"])

        if options["only_avatars"]:
            self.stdout.write(self.style.SUCCESS("Avatar layer assets regenerated."))
            return

        texts = Text.objects.select_related("level", "category", "character").order_by("id")
        if options["limit"]:
            texts = texts[: options["limit"]]

        processed = 0
        warnings = 0
        for text in texts.iterator():
            processed += 1
            text_word_count = word_count(text.content_en)
            min_words, max_words = LEVEL_WORD_LIMITS.get(text.level.slug, (0, 99999))
            repaired_story = False
            if not (min_words <= text_word_count <= max_words):
                warnings += 1
                if warnings <= options["warning_limit"]:
                    self.stdout.write(
                        self.style.WARNING(
                            f"{text.slug}: {text_word_count} words outside {text.level.slug} range {min_words}-{max_words}."
                        )
                    )
                if options["repair_stories"]:
                    text.content_en = enforce_level_word_limits(
                        text.content_en,
                        text.level.slug,
                        self.context_for_text(text),
                    )
                    text_word_count = word_count(text.content_en)
                    repaired_story = True

            changed_fields = []
            if repaired_story:
                changed_fields.append("content_en")
            if text.word_count != text_word_count:
                text.word_count = text_word_count
                changed_fields.append("word_count")

            if text.image_canvas_width != 500:
                text.image_canvas_width = 500
                changed_fields.append("image_canvas_width")
            if text.image_canvas_height != 500:
                text.image_canvas_height = 500
                changed_fields.append("image_canvas_height")

            if not options["skip_prompts"]:
                prompt = build_image_prompt(text)
                if text.image_prompt != prompt:
                    text.image_prompt = prompt
                    changed_fields.append("image_prompt")

            if changed_fields and not options["dry_run"]:
                changed_fields = list(dict.fromkeys(changed_fields))
                text.save(update_fields=changed_fields)

            if not options["skip_images"] and not options["dry_run"]:
                animation_path = write_text_illustration(text)
                if text.animation_asset.name != animation_path:
                    text.animation_asset = animation_path
                    text.save(update_fields=["animation_asset"])

            if not options["skip_vocabulary"] and not options["dry_run"]:
                replace_text_vocabulary(
                    text,
                    max_items=options["max_vocab"],
                    frequency_words=frequency_words,
                    source="dynamic_nlp",
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"Mass content generation finished: {processed} texts processed, {warnings} word-limit warnings."
            )
        )
        if warnings > options["warning_limit"]:
            hidden = warnings - options["warning_limit"]
            self.stdout.write(f"{hidden} additional word-limit warnings hidden. Use --warning-limit to change this.")

    def context_for_text(self, text):
        title_words = [word.strip(":-").lower() for word in text.title.split() if len(word.strip(":-")) > 3]
        object_word = title_words[-1] if title_words else "detail"
        return {
            "subject": text.character.name if text.character else "the reader",
            "helper": "friend",
            "value": text.category.name.lower(),
            "object_word": object_word,
            "place_word": text.category.name.lower(),
        }

    def seed_avatar_layers(self, dry_run=False):
        active_keys = {(name, option_type) for name, option_type, _, _, _ in AVATAR_LAYER_OPTIONS}
        if not dry_run:
            for option in AvatarOption.objects.exclude(option_type="preset"):
                if (option.name, option.option_type) not in active_keys:
                    option.is_active = False
                    option.save(update_fields=["is_active"])

        for name, option_type, image_asset, coin_price, layer_order in AVATAR_LAYER_OPTIONS:
            if dry_run:
                continue
            category_slug, required_reads = AVATAR_CATEGORY_REQUIREMENTS.get(name, (None, 0))
            required_category = Category.objects.filter(slug=category_slug).first() if category_slug else None
            option, _ = AvatarOption.objects.update_or_create(
                name=name,
                option_type=option_type,
                defaults={
                    "image_asset": image_asset,
                    "coin_price": coin_price,
                    "layer_order": layer_order,
                    "required_category": required_category,
                    "required_category_reads": required_reads if required_category else 0,
                    "is_active": True,
                },
            )
            self.write_avatar_layer_asset(option)

    def write_avatar_layer_asset(self, option):
        if not option.image_asset:
            return

        full_path = Path(settings.MEDIA_ROOT) / option.image_asset.name
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(self.avatar_svg(option), encoding="utf-8")

    def avatar_svg(self, option):
        return build_cartoon_avatar_svg(option)

    def legacy_avatar_svg(self, option):
        palette = {
            "skin_light": "#F2BE8F",
            "skin_medium": "#C98259",
            "skin_dark": "#86543F",
            "skin_gold": "#D9B97E",
            "blue": "#1C4259",
            "teal": "#2F8F8B",
            "gold": "#D9B97E",
            "caramel": "#BF9663",
            "brown": "#8C613B",
            "coral": "#D86F45",
            "violet": "#6F4E8C",
            "navy": "#26314F",
            "paper": "#F2F2EB",
        }
        name = option.name.lower()

        if option.option_type == "base_body":
            if "media" in name:
                skin = palette["skin_medium"]
                bg = "#E7EEF1"
            elif "escura" in name:
                skin = palette["skin_dark"]
                bg = "#EDE7F3"
            elif "quente" in name:
                skin = "#B76F4C"
                bg = "#F3E9DF"
            elif "dourada" in name:
                skin = palette["skin_gold"]
                bg = "#F6F0DD"
            else:
                skin = palette["skin_light"]
                bg = "#EAF3F4"
            shape = f"""
<circle cx="250" cy="250" r="205" fill="{bg}"/>
<circle cx="250" cy="250" r="196" fill="#FFFFFF" opacity=".20"/>
<ellipse cx="250" cy="436" rx="104" ry="22" fill="#1C4259" opacity=".16"/>
<path d="M150 438 C166 334 334 334 350 438 Z" fill="url(#outfitGrad)"/>
<path d="M212 324 C224 292 276 292 288 324 L284 354 C266 366 234 366 216 354 Z" fill="url(#skinGrad)"/>
<ellipse cx="250" cy="205" rx="78" ry="86" fill="url(#skinGrad)"/>
<ellipse cx="180" cy="214" rx="14" ry="19" fill="url(#skinGrad)"/>
<ellipse cx="320" cy="214" rx="14" ry="19" fill="url(#skinGrad)"/>
<path d="M177 210 C184 210 186 220 180 226" fill="none" stroke="#8C613B" stroke-width="4" stroke-linecap="round" opacity=".18"/>
<path d="M323 210 C316 210 314 220 320 226" fill="none" stroke="#8C613B" stroke-width="4" stroke-linecap="round" opacity=".18"/>
<ellipse cx="224" cy="190" rx="24" ry="13" fill="#FFFFFF" opacity=".20"/>
<ellipse cx="219" cy="235" rx="17" ry="9" fill="#D86F45" opacity=".14"/>
<ellipse cx="281" cy="235" rx="17" ry="9" fill="#D86F45" opacity=".14"/>
<path d="M250 204 C243 226 243 239 254 244" fill="none" stroke="#8C613B" stroke-width="4" stroke-linecap="round" opacity=".24"/>
<path d="M214 274 C234 292 266 292 286 274 C280 304 220 304 214 274 Z" fill="#1C4259" opacity=".10"/>
<path d="M208 338 C228 354 272 354 292 338" fill="none" stroke="#1C4259" stroke-width="8" stroke-linecap="round" opacity=".10"/>
"""
        elif option.option_type == "body_style":
            if "feminino" in name:
                shape = f"""
<circle cx="206" cy="238" r="7" fill="#D86F45" opacity=".18"/>
<circle cx="294" cy="238" r="7" fill="#D86F45" opacity=".18"/>
<path d="M205 334 C224 318 276 318 295 334" fill="none" stroke="#D9B97E" stroke-width="7" stroke-linecap="round" opacity=".72"/>
"""
            else:
                shape = f"""
<path d="M211 276 C231 292 269 292 289 276" fill="none" stroke="#1C4259" stroke-width="5" stroke-linecap="round" opacity=".20"/>
<path d="M200 336 C222 320 278 320 300 336" fill="none" stroke="#1C4259" stroke-width="7" stroke-linecap="round" opacity=".18"/>
"""
        elif option.option_type == "hair_style":
            if "turquesa" in name:
                shape = f"""
<path d="M170 177 C176 108 262 82 326 134 C326 188 292 220 236 220 C208 220 184 204 170 177 Z" fill="url(#hairDepth)"/>
<path d="M218 126 C198 142 190 164 192 196 C232 171 276 160 318 166 C306 130 270 112 218 126 Z" fill="#44A8A3" opacity=".82"/>
"""
            elif "laranja" in name:
                shape = f"""
<path d="M170 166 C184 92 304 88 330 166 C344 246 314 318 280 354 L264 288 C306 280 316 228 296 176 C262 154 216 156 180 184 Z" fill="url(#hairDepth)"/>
<path d="M180 176 C214 124 286 124 316 176 C270 156 224 156 180 176 Z" fill="#F07A50" opacity=".9"/>
"""
            elif "cacheado" in name:
                shape = f"""
<circle cx="184" cy="168" r="28" fill="url(#hairDepth)"/>
<circle cx="218" cy="128" r="32" fill="url(#hairDepth)"/>
<circle cx="260" cy="124" r="36" fill="url(#hairDepth)"/>
<circle cx="304" cy="156" r="32" fill="url(#hairDepth)"/>
<path d="M172 188 C202 154 288 154 328 188 C302 174 218 174 172 188 Z" fill="#7A4E34"/>
"""
            elif "preto longo" in name:
                shape = f"""
<path d="M162 168 C168 92 332 92 338 168 L330 312 C298 342 202 342 170 312 Z" fill="url(#hairDepth)"/>
<path d="M178 168 C212 130 288 130 322 168 C280 152 220 152 178 168 Z" fill="#26314F"/>
"""
            elif "castanho" in name:
                shape = f"""
<path d="M164 184 C174 108 326 104 336 184 C302 158 204 158 164 184 Z" fill="url(#hairDepth)"/>
<path d="M176 194 C206 158 270 148 324 190 C276 180 224 184 176 194 Z" fill="#A06A43" opacity=".9"/>
"""
            elif "careca" in name:
                shape = f"""
<path d="M190 178 C214 146 286 146 310 178" fill="none" stroke="#BF9663" stroke-width="7" stroke-linecap="round" opacity=".45"/>
<path d="M184 196 C220 178 280 178 316 196" fill="none" stroke="#1C4259" stroke-width="5" stroke-linecap="round" opacity=".22"/>
"""
            elif "lenco" in name:
                shape = f"""
<path d="M156 178 C164 98 336 98 344 178 L344 306 C302 334 198 334 156 306 Z" fill="url(#hairDepth)"/>
<path d="M178 174 C206 136 294 136 322 174 C280 158 220 158 178 174 Z" fill="#8B63A5"/>
<rect x="306" y="246" width="42" height="76" rx="20" fill="{palette['violet']}"/>
"""
            else:
                shape = f"""
<path d="M164 184 C174 104 326 98 336 184 C302 156 204 156 164 184 Z" fill="url(#hairDepth)"/>
<path d="M176 192 C206 150 288 146 324 188 C286 176 226 180 176 192 Z" fill="#204E6B" opacity=".9"/>
"""
        elif option.option_type == "eyes":
            if "felizes" in name:
                shape = f"""
<path d="M212 214 C222 205 232 205 242 214" fill="none" stroke="{palette['blue']}" stroke-width="7" stroke-linecap="round"/>
<path d="M258 214 C268 205 278 205 288 214" fill="none" stroke="{palette['blue']}" stroke-width="7" stroke-linecap="round"/>
<path d="M222 248 C240 264 260 264 278 248" fill="none" stroke="{palette['blue']}" stroke-width="7" stroke-linecap="round"/>
"""
            elif "serenos" in name:
                shape = f"""
<path d="M214 216 H240" stroke="{palette['blue']}" stroke-width="6" stroke-linecap="round"/>
<path d="M260 216 H286" stroke="{palette['blue']}" stroke-width="6" stroke-linecap="round"/>
<path d="M228 250 C242 258 258 258 272 250" fill="none" stroke="{palette['blue']}" stroke-width="6" stroke-linecap="round"/>
"""
            elif "piscadinha" in name:
                shape = f"""
<circle cx="228" cy="216" r="9" fill="{palette['blue']}"/>
<circle cx="231" cy="213" r="3" fill="#FFFFFF"/>
<path d="M260 216 H286" stroke="{palette['blue']}" stroke-width="7" stroke-linecap="round"/>
<path d="M226 250 C242 262 260 262 276 250" fill="none" stroke="{palette['blue']}" stroke-width="7" stroke-linecap="round"/>
"""
            elif "focados" in name:
                shape = f"""
<circle cx="228" cy="216" r="9" fill="{palette['blue']}"/>
<circle cx="272" cy="216" r="9" fill="{palette['blue']}"/>
<path d="M210 201 L241 206 M259 206 L290 201" stroke="{palette['blue']}" stroke-width="6" stroke-linecap="round"/>
<path d="M230 250 C244 256 256 256 270 250" fill="none" stroke="{palette['blue']}" stroke-width="6" stroke-linecap="round"/>
"""
            else:
                shape = f"""
<circle cx="228" cy="216" r="10" fill="{palette['blue']}"/>
<circle cx="272" cy="216" r="10" fill="{palette['blue']}"/>
<circle cx="231" cy="212" r="3.5" fill="#FFFFFF"/>
<circle cx="275" cy="212" r="3.5" fill="#FFFFFF"/>
<path d="M226 250 C242 262 258 262 274 250" fill="none" stroke="{palette['blue']}" stroke-width="7" stroke-linecap="round"/>
"""
        elif option.option_type == "outfit":
            if "coral" in name:
                fill = palette["coral"]
                detail = palette["gold"]
            elif "violeta" in name:
                fill = palette["violet"]
                detail = palette["paper"]
            elif "turquesa" in name:
                fill = palette["teal"]
                detail = palette["paper"]
            elif "jaqueta" in name:
                fill = palette["navy"]
                detail = palette["gold"]
            elif "sueter" in name:
                fill = palette["gold"]
                detail = palette["blue"]
            elif "cachecol" in name:
                fill = palette["blue"]
                detail = palette["gold"]
            else:
                fill = palette["blue"]
                detail = palette["gold"]
            extra = ""
            if "cachecol" in name:
                extra = f'<path d="M184 318 C220 294 284 294 318 318 L306 352 C276 332 224 332 194 352 Z" fill="{detail}"/>'
            elif "jaqueta" in name:
                extra = f'<path d="M206 326 V430 M294 326 V430" stroke="{detail}" stroke-width="8" stroke-linecap="round"/><circle cx="250" cy="362" r="8" fill="{detail}"/>'
            elif "sueter" in name:
                extra = f'<path d="M190 358 H310" stroke="{detail}" stroke-width="9" stroke-linecap="round" opacity=".8"/>'
            shape = f"""
<path d="M150 438 C170 330 330 330 350 438 Z" fill="url(#outfitGrad)"/>
<path d="M207 326 L250 376 L293 326" fill="none" stroke="{detail}" stroke-width="9" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M186 374 C214 346 286 346 314 374" fill="none" stroke="#FFFFFF" stroke-width="9" stroke-linecap="round" opacity=".14"/>
{extra}
"""
        else:
            if "oculos" in name:
                shape = f"""
<circle cx="228" cy="216" r="19" fill="none" stroke="{palette['caramel']}" stroke-width="5"/>
<circle cx="272" cy="216" r="19" fill="none" stroke="{palette['caramel']}" stroke-width="5"/>
<path d="M247 216 H253" stroke="{palette['caramel']}" stroke-width="5" stroke-linecap="round"/>
"""
            elif "fones" in name:
                shape = f"""
<path d="M178 212 C178 132 322 132 322 212" fill="none" stroke="{palette['blue']}" stroke-width="10" stroke-linecap="round"/>
<rect x="154" y="204" width="32" height="56" rx="15" fill="{palette['teal']}"/>
<rect x="314" y="204" width="32" height="56" rx="15" fill="{palette['teal']}"/>
"""
            elif "brinco" in name:
                shape = f"""
<circle cx="182" cy="236" r="6" fill="{palette['gold']}"/>
<circle cx="318" cy="236" r="6" fill="{palette['gold']}"/>
<circle cx="182" cy="252" r="5" fill="{palette['gold']}" opacity=".75"/>
<circle cx="318" cy="252" r="5" fill="{palette['gold']}" opacity=".75"/>
"""
            elif "gravata" in name:
                shape = f"""
<path d="M224 344 L250 328 L276 344 L250 360 Z" fill="{palette['coral']}"/>
<path d="M250 360 L266 410 H234 Z" fill="{palette['coral']}"/>
"""
            elif "gorro" in name:
                shape = f"""
<path d="M180 142 H320 L250 92 Z" fill="{palette['blue']}"/>
<rect x="190" y="140" width="120" height="16" rx="8" fill="{palette['gold']}"/>
<path d="M318 142 C350 158 350 192 318 208" fill="none" stroke="{palette['gold']}" stroke-width="8"/>
"""
            else:
                shape = f"""
<rect x="326" y="274" width="54" height="74" rx="10" fill="{palette['gold']}" stroke="{palette['brown']}" stroke-width="7"/>
<path d="M340 296 H364 M340 314 H360" stroke="{palette['brown']}" stroke-width="5" stroke-linecap="round"/>
"""

        skin_for_grad = locals().get("skin", palette["skin_light"])
        outfit_for_grad = locals().get("fill", palette["blue"])
        hair_for_grad = {
            "turquesa": palette["teal"],
            "laranja": palette["coral"],
            "cacheado": palette["brown"],
            "preto": "#18222B",
            "castanho": palette["brown"],
            "lenco": palette["violet"],
        }
        hair_grad = next((color for key, color in hair_for_grad.items() if key in name), palette["blue"])

        if option.option_type == "hair_style":
            shape += f"""
<path d="M190 152 C222 112 282 112 314 152" fill="none" stroke="#FFFFFF" stroke-width="12" stroke-linecap="round" opacity=".18"/>
"""
        elif option.option_type == "accessory":
            shape += """
<circle cx="182" cy="154" r="18" fill="#FFFFFF" opacity=".14"/>
"""

        defs = f"""
<defs>
  <radialGradient id="skinGrad" cx="34%" cy="24%" r="78%">
    <stop offset="0" stop-color="#FFFFFF" stop-opacity=".58"/>
    <stop offset=".34" stop-color="{skin_for_grad}"/>
    <stop offset="1" stop-color="#8C613B" stop-opacity=".42"/>
  </radialGradient>
  <linearGradient id="outfitGrad" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="#FFFFFF" stop-opacity=".26"/>
    <stop offset=".28" stop-color="{outfit_for_grad}"/>
    <stop offset="1" stop-color="#102B3A"/>
  </linearGradient>
  <linearGradient id="hairDepth" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="#FFFFFF" stop-opacity=".18"/>
    <stop offset=".34" stop-color="{hair_grad}"/>
    <stop offset="1" stop-color="#1B1F2D"/>
  </linearGradient>
  <filter id="avatarDepth" x="-20%" y="-20%" width="140%" height="140%">
    <feDropShadow dx="0" dy="10" stdDeviation="10" flood-color="#1C4259" flood-opacity=".18"/>
  </filter>
</defs>
"""

        return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 500 500" width="500" height="500" role="img" aria-label="{option.name}">
<title>{option.name}</title>
{defs}
<g filter="url(#avatarDepth)">
{shape}
</g>
</svg>
"""
