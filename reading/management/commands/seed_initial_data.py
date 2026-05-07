from django.core.management.base import BaseCommand

from accounts.models import AvatarOption
from progress.models import Achievement
from reading.models import Category, Character, Level


class Command(BaseCommand):
    help = "Create initial Lecto levels, categories, characters, avatars, and achievements."

    def handle(self, *args, **options):
        self.seed_levels()
        self.seed_categories()
        self.seed_characters()
        self.seed_avatars()
        self.seed_achievements()
        self.stdout.write(self.style.SUCCESS("Lecto initial data ready."))

    def seed_levels(self):
        levels = [
            ("Iniciante", "iniciante", 1, 40, 80),
            ("A1", "a1", 2, 80, 120),
            ("A2", "a2", 3, 120, 180),
            ("B1", "b1", 4, 180, 260),
            ("B2", "b2", 5, 260, 380),
            ("C1", "c1", 6, 380, 550),
            ("C2", "c2", 7, 550, 750),
        ]

        for name, slug, order, min_words, max_words in levels:
            Level.objects.update_or_create(
                slug=slug,
                defaults={
                    "name": name,
                    "order": order,
                    "description_pt": f"Textos de leitura em ingles para o nivel {name}.",
                    "min_words": min_words,
                    "max_words": max_words,
                },
            )

    def seed_categories(self):
        categories = [
            ("Contos", "contos"),
            ("Cultura pop", "cultura-pop"),
            ("Anime", "anime"),
            ("HQs", "hqs"),
            ("Tecnologia", "tecnologia"),
            ("Viagens", "viagens"),
            ("Musica", "musica"),
            ("Series", "series"),
            ("Games", "games"),
            ("Meio ambiente", "meio-ambiente"),
            ("Saude e bem-estar", "saude-e-bem-estar"),
            ("Cotidiano", "cotidiano"),
        ]

        for name, slug in categories:
            Category.objects.update_or_create(
                slug=slug,
                defaults={
                    "name": name,
                    "description_pt": f"Textos em ingles sobre {name.lower()}.",
                    "is_active": True,
                },
            )

    def seed_characters(self):
        characters = [
            ("Spider-Man", "spider-man", "marvel"),
            ("Iron Man", "iron-man", "marvel"),
            ("Captain America", "captain-america", "marvel"),
            ("Thor", "thor", "marvel"),
            ("Hulk", "hulk", "marvel"),
            ("Black Panther", "black-panther", "marvel"),
            ("Doctor Strange", "doctor-strange", "marvel"),
            ("Wolverine", "wolverine", "marvel"),
            ("Deadpool", "deadpool", "marvel"),
            ("Captain Marvel", "captain-marvel", "marvel"),
            ("Superman", "superman", "dc"),
            ("Batman", "batman", "dc"),
            ("Wonder Woman", "wonder-woman", "dc"),
            ("The Flash", "the-flash", "dc"),
            ("Aquaman", "aquaman", "dc"),
            ("Green Lantern", "green-lantern", "dc"),
            ("Green Arrow", "green-arrow", "dc"),
            ("Cyborg", "cyborg", "dc"),
            ("Harley Quinn", "harley-quinn", "dc"),
            ("Joker", "joker", "dc"),
        ]

        for name, slug, publisher in characters:
            Character.objects.update_or_create(
                slug=slug,
                defaults={
                    "name": name,
                    "publisher": publisher,
                    "description_pt": f"Texto original e curto sobre {name}.",
                    "is_active": True,
                },
            )

    def seed_avatars(self):
        options = [
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
        category_requirements = {
            "Base dourada Lecto": ("cotidiano", 10),
            "Lenco violeta": ("cultura-pop", 10),
            "Cachecol dourado": ("viagens", 10),
            "Fones azul": ("tecnologia", 10),
            "Gorro academico": ("cotidiano", 10),
            "Livro lateral": ("contos", 10),
        }

        for name, option_type, image_asset, coin_price, layer_order in options:
            category_slug, required_reads = category_requirements.get(name, (None, 0))
            required_category = Category.objects.filter(slug=category_slug).first() if category_slug else None
            AvatarOption.objects.update_or_create(
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

    def seed_achievements(self):
        achievements = [
            ("Primeiro texto lido", "primeiro-texto-lido", 10),
            ("Primeiro quiz concluido", "primeiro-quiz-concluido", 10),
            ("5 textos lidos", "5-textos-lidos", 15),
            ("10 textos lidos", "10-textos-lidos", 25),
            ("Primeiro favorito", "primeiro-favorito", 5),
            ("Primeira semana ativa", "primeira-semana-ativa", 30),
        ]

        for name, slug, coin_reward in achievements:
            Achievement.objects.update_or_create(
                slug=slug,
                defaults={
                    "name": name,
                    "description_pt": name,
                    "coin_reward": coin_reward,
                    "is_active": True,
                },
            )
