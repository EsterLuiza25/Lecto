from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.text import slugify

from quiz.models import (
    PlacementQuizAnswer,
    PlacementQuizQuestion,
    TextQuizAnswer,
    TextQuizQuestion,
)
from reading.artwork import write_text_illustration
from reading.content_pipeline import (
    build_image_prompt,
    enforce_level_word_limits,
    replace_text_vocabulary,
    word_count as count_words,
)
from reading.models import Category, Character, Level, Text, VocabularyItem


TOPICS = [
    ("Morning Light", "yard", "light"),
    ("Blue Bag", "school", "bag"),
    ("Small Map", "street", "map"),
    ("New Song", "music", "song"),
    ("Kind Note", "library", "note"),
    ("Green Park", "park", "tree"),
    ("Quiet Room", "home", "room"),
    ("Open Door", "house", "door"),
    ("Fast Bus", "city", "bus"),
    ("Warm Tea", "kitchen", "tea"),
    ("Good Team", "field", "team"),
    ("Red Kite", "beach", "kite"),
    ("Silver Key", "desk", "key"),
    ("Happy Cat", "garden", "cat"),
    ("First Star", "night", "star"),
    ("Clean River", "river", "water"),
    ("New Game", "table", "game"),
    ("Bright Screen", "office", "screen"),
    ("Old Photo", "album", "photo"),
    ("Long Road", "trip", "road"),
    ("Friendly Robot", "lab", "robot"),
    ("Safe Bridge", "town", "bridge"),
    ("Yellow Train", "station", "train"),
    ("Sweet Cake", "shop", "cake"),
    ("Hidden Box", "room", "box"),
    ("Good Idea", "class", "idea"),
    ("Fresh Rain", "street", "rain"),
    ("Careful Plan", "desk", "plan"),
    ("Brave Voice", "stage", "voice"),
    ("Final Page", "library", "page"),
]


CATEGORY_CONTEXT = {
    "anime": ("Lia", "training room", "friend", "practice"),
    "biografias-curtas": ("Ana", "small studio", "teacher", "dream"),
    "carreira-e-estudos": ("Noah", "study desk", "classmate", "goal"),
    "ciencia": ("Mia", "science room", "teacher", "test"),
    "cinema": ("Leo", "movie room", "director", "scene"),
    "contos": ("Luna", "quiet village", "friend", "story"),
    "cotidiano": ("Tom", "busy street", "neighbor", "day"),
    "cultura-pop": ("Eva", "online club", "friend", "trend"),
    "esportes": ("Max", "sports field", "coach", "match"),
    "games": ("Ivy", "game room", "team", "level"),
    "historia": ("Nina", "old museum", "guide", "past"),
    "hqs": ("Alex", "city roof", "hero", "choice"),
    "materias": ("Ben", "classroom", "teacher", "lesson"),
    "meio-ambiente": ("Sofia", "green path", "group", "nature"),
    "misterios-e-curiosidades": ("Oli", "old museum", "friend", "clue"),
    "musica": ("Nora", "music room", "band", "sound"),
    "noticias": ("Rafa", "school hall", "reporter", "news"),
    "saude-e-bem-estar": ("Maya", "calm studio", "coach", "habit"),
    "series": ("Kai", "living room", "sister", "episode"),
    "tecnologia": ("Theo", "small lab", "robot", "tool"),
    "viagens": ("Rio", "train station", "family", "trip"),
}


LEVEL_META = {
    "iniciante": {"target": 42, "name": "Iniciante"},
    "a1": {"target": 62, "name": "A1"},
    "a2": {"target": 88, "name": "A2"},
    "b1": {"target": 130, "name": "B1"},
    "b2": {"target": 180, "name": "B2"},
    "c1": {"target": 245, "name": "C1"},
    "c2": {"target": 310, "name": "C2"},
}


VOCAB_POOLS = {
    "iniciante": [
        ("bag", "bolsa", "beg"),
        ("book", "livro", "buk"),
        ("cat", "gato", "ket"),
        ("day", "dia", "dei"),
        ("door", "porta", "dor"),
        ("friend", "amigo", "frend"),
        ("go", "ir", "gou"),
        ("good", "bom", "gud"),
        ("help", "ajudar", "help"),
        ("home", "casa", "roum"),
        ("look", "olhar", "luk"),
        ("map", "mapa", "mep"),
        ("new", "novo", "niu"),
        ("park", "parque", "park"),
        ("read", "ler", "rid"),
        ("room", "quarto/sala", "rum"),
        ("safe", "seguro", "seif"),
        ("small", "pequeno", "smol"),
        ("smile", "sorrir", "smail"),
        ("water", "agua", "uo-ter"),
    ],
    "a1": [
        ("after", "depois", "af-ter"),
        ("always", "sempre", "ol-ueiz"),
        ("ask", "perguntar", "esk"),
        ("bring", "trazer", "bring"),
        ("city", "cidade", "si-ti"),
        ("clean", "limpo", "clin"),
        ("early", "cedo", "er-li"),
        ("family", "familia", "fe-mi-li"),
        ("learn", "aprender", "lern"),
        ("listen", "escutar", "li-sen"),
        ("meet", "encontrar", "mit"),
        ("near", "perto", "nir"),
        ("place", "lugar", "pleis"),
        ("school", "escola", "skul"),
        ("start", "comecar", "start"),
        ("table", "mesa", "tei-bol"),
        ("teacher", "professor", "ti-tcher"),
        ("today", "hoje", "tu-dei"),
        ("together", "juntos", "tu-gue-der"),
        ("walk", "andar", "uok"),
    ],
    "a2": [
        ("arrive", "chegar", "a-raiv"),
        ("because", "porque", "bi-coz"),
        ("before", "antes", "bi-for"),
        ("careful", "cuidadoso", "ker-ful"),
        ("change", "mudar", "tcheinj"),
        ("choose", "escolher", "tchuz"),
        ("clear", "claro", "clir"),
        ("different", "diferente", "di-fe-rent"),
        ("enough", "suficiente", "i-nof"),
        ("explain", "explicar", "eks-plein"),
        ("later", "mais tarde", "lei-ter"),
        ("message", "mensagem", "me-sij"),
        ("problem", "problema", "pro-blem"),
        ("quickly", "rapidamente", "kui-kli"),
        ("ready", "pronto", "re-di"),
        ("share", "compartilhar", "sher"),
        ("suddenly", "de repente", "sa-den-li"),
        ("understand", "entender", "an-der-stend"),
        ("useful", "util", "ius-ful"),
        ("without", "sem", "ui-daut"),
    ],
    "b1": [
        ("advice", "conselho", "ad-vais"),
        ("although", "embora", "ol-dou"),
        ("believe", "acreditar", "bi-liv"),
        ("decision", "decisao", "di-si-jon"),
        ("effort", "esforco", "e-fort"),
        ("improve", "melhorar", "im-pruv"),
        ("instead", "em vez disso", "in-sted"),
        ("manage", "conseguir administrar", "me-nedj"),
        ("mistake", "erro", "mis-teik"),
        ("notice", "perceber", "nou-tis"),
        ("opinion", "opiniao", "o-pi-ni-on"),
        ("practice", "pratica", "prak-tis"),
        ("reason", "razao", "ri-zon"),
        ("result", "resultado", "ri-zolt"),
        ("support", "apoio", "su-port"),
        ("toward", "em direcao a", "tor-d"),
        ("trust", "confiar", "trast"),
        ("usually", "geralmente", "iu-ju-a-li"),
        ("value", "valor", "ve-liu"),
        ("wonder", "imaginar", "uan-der"),
    ],
    "b2": [
        ("approach", "abordagem", "a-proutch"),
        ("assume", "presumir", "a-sum"),
        ("balance", "equilibrio", "ba-lans"),
        ("challenge", "desafio", "tcha-lendj"),
        ("compare", "comparar", "com-per"),
        ("complex", "complexo", "com-pleks"),
        ("consequence", "consequencia", "con-si-kuens"),
        ("evidence", "evidencia", "e-vi-dens"),
        ("however", "no entanto", "hau-e-ver"),
        ("impact", "impacto", "im-pact"),
        ("influence", "influencia", "in-flu-ens"),
        ("pattern", "padrao", "pa-tern"),
        ("reliable", "confiavel", "ri-lai-a-bol"),
        ("respond", "responder", "ri-spond"),
        ("risk", "risco", "risk"),
        ("strategy", "estrategia", "stra-te-dji"),
        ("suggest", "sugerir", "sa-djest"),
        ("tension", "tensao", "ten-shon"),
        ("therefore", "portanto", "der-for"),
        ("trade-off", "compensacao", "treid-of"),
    ],
    "c1": [
        ("adapt", "adaptar", "a-dapt"),
        ("constraint", "restricao", "con-streint"),
        ("emphasis", "enfase", "em-fa-sis"),
        ("framework", "estrutura conceitual", "freim-uork"),
        ("insight", "percepcao", "in-sait"),
        ("layered", "em camadas", "lei-erd"),
        ("maintain", "manter", "mein-tein"),
        ("nuance", "nuance", "niu-ans"),
        ("perspective", "perspectiva", "per-spec-tiv"),
        ("precise", "preciso", "pri-sais"),
        ("priority", "prioridade", "prai-o-ri-ti"),
        ("question", "questionar", "kues-tchon"),
        ("reinforce", "reforcar", "ri-in-fors"),
        ("reshape", "remodelar", "ri-sheip"),
        ("subtle", "sutil", "sa-tol"),
        ("sustain", "sustentar", "sus-tein"),
        ("tendency", "tendencia", "ten-den-si"),
        ("underlying", "subjacente", "an-der-lai-ing"),
        ("viable", "viavel", "vai-a-bol"),
        ("widely", "amplamente", "uaid-li"),
    ],
    "c2": [
        ("ambiguity", "ambiguidade", "am-bi-giu-i-ti"),
        ("coherence", "coerencia", "cou-rir-ens"),
        ("discern", "discernir", "di-sern"),
        ("elaborate", "elaborar", "i-la-bo-reit"),
        ("friction", "atrito", "frik-shon"),
        ("implication", "implicacao", "im-pli-kei-shon"),
        ("meticulous", "meticuloso", "me-ti-kiu-lus"),
        ("paradox", "paradoxo", "pa-ra-doks"),
        ("provisional", "provisorio", "pro-vi-jo-nal"),
        ("reconcile", "reconciliar", "re-con-sail"),
        ("resilience", "resiliencia", "ri-zi-li-ens"),
        ("scrutiny", "analise minuciosa", "skru-ti-ni"),
        ("speculative", "especulativo", "spe-kiu-la-tiv"),
        ("temper", "moderar", "tem-per"),
        ("threshold", "limiar", "thresh-hold"),
        ("unfold", "desdobrar", "an-fold"),
        ("volatile", "instavel", "vo-la-til"),
        ("warrant", "justificar", "uo-rant"),
        ("yield", "produzir/ceder", "iild"),
        ("zeal", "entusiasmo", "zil"),
    ],
}


PLACEMENT_DATA = {
    "iniciante": [
        ("I am Ana.", "Ana esta se apresentando.", "Ana esta viajando.", "Ana esta comprando pao.", "Ana esta dormindo."),
        ("The book is blue.", "O livro e azul.", "O livro e grande.", "A bolsa e azul.", "O caderno e novo."),
        ("Tom has a cat.", "Tom tem um gato.", "Tom ve um carro.", "Tom gosta de cha.", "Tom perdeu um mapa."),
        ("We read at home.", "Nos lemos em casa.", "Nos corremos no parque.", "Eles leem na escola.", "Eu estudo de noite."),
        ("The door is open.", "A porta esta aberta.", "A janela e pequena.", "O quarto esta frio.", "A chave esta na mesa."),
        ("She likes water.", "Ela gosta de agua.", "Ela vende agua.", "Ela bebe cafe.", "Ela limpa a rua."),
        ("They are friends.", "Eles sao amigos.", "Eles sao professores.", "Eles estao atrasados.", "Eles estao perdidos."),
    ],
    "a1": [
        ("Mia walks to school every day.", "Mia vai andando para a escola todos os dias.", "Mia trabalha de noite.", "Mia viaja todo mes.", "Mia cozinha na escola."),
        ("The teacher asks a simple question.", "O professor faz uma pergunta simples.", "O aluno fecha a porta.", "O professor compra um livro.", "A pergunta e impossivel."),
        ("I meet my friend after lunch.", "Eu encontro meu amigo depois do almoco.", "Eu estudo antes do cafe.", "Eu durmo depois da aula.", "Eu jogo antes do almoco."),
        ("The family eats together on Sunday.", "A familia come junta no domingo.", "A familia corre na segunda.", "A familia viaja no inverno.", "A familia canta na escola."),
        ("This place is clean and quiet.", "Este lugar e limpo e calmo.", "Este lugar e caro e longe.", "Esse parque e frio.", "A sala esta cheia."),
        ("Nora listens to a new song.", "Nora escuta uma musica nova.", "Nora escreve uma musica antiga.", "Nora compra um jogo.", "Nora ve uma ponte."),
        ("The bus starts early today.", "O onibus sai cedo hoje.", "O trem chega tarde sempre.", "O carro para aqui.", "O onibus esta quebrado."),
    ],
    "a2": [
        ("Leo arrived late because the train stopped.", "Leo chegou tarde porque o trem parou.", "Leo saiu cedo porque choveu.", "Leo perdeu o trem porque dormiu.", "Leo chegou cedo porque correu."),
        ("Before the game, the team made a careful plan.", "Antes do jogo, o time fez um plano cuidadoso.", "Depois do jogo, o time esqueceu o plano.", "Durante a aula, o time fez um bolo.", "Antes da viagem, o professor cantou."),
        ("The message was useful, so Ana shared it.", "A mensagem foi util, entao Ana a compartilhou.", "A mensagem era longa, entao Ana dormiu.", "A mensagem era falsa, entao Ana correu.", "A mensagem sumiu antes de Ana ler."),
        ("They chose the quiet room because it was easier to read.", "Eles escolheram a sala calma porque era mais facil ler.", "Eles escolheram a rua porque era barulhenta.", "Eles escolheram o trem porque estava vazio.", "Eles escolheram o parque porque era perigoso."),
        ("The robot suddenly moved across the table.", "O robo de repente se moveu pela mesa.", "O robo nunca funcionou.", "O robo cantou no jardim.", "O robo escreveu uma carta."),
        ("The guide explained the map clearly.", "O guia explicou o mapa claramente.", "O guia rasgou o mapa.", "O aluno perdeu o mapa.", "A guia fechou a janela."),
        ("After the rain, the street looked different.", "Depois da chuva, a rua parecia diferente.", "Antes da chuva, a praia estava seca.", "Depois do sol, o quarto sumiu.", "A rua nunca mudou."),
    ],
    "b1": [
        ("Although the plan was simple, it helped the group avoid a common mistake.", "Embora o plano fosse simples, ajudou o grupo a evitar um erro comum.", "O plano era secreto e impossivel.", "O grupo ignorou todos os erros.", "O plano foi cancelado antes de comecar."),
        ("The main reason for the decision was trust.", "A principal razao da decisao foi confianca.", "A decisao foi tomada por acidente.", "A razao principal foi medo de livros.", "A decisao nao tinha nenhuma razao."),
        ("Practice improved her result more than luck did.", "A pratica melhorou o resultado dela mais do que a sorte.", "A sorte sempre venceu a pratica.", "O resultado piorou por causa da pratica.", "Ela nao tentou melhorar."),
        ("Instead of arguing, they listened to advice.", "Em vez de discutir, eles ouviram conselhos.", "Eles discutiram sem parar.", "Eles recusaram qualquer ajuda.", "Eles esqueceram o conselho."),
        ("The text suggests that small effort can change a day.", "O texto sugere que pequeno esforco pode mudar um dia.", "O texto diz que esforco nao importa.", "O texto fala apenas de dinheiro.", "O texto nega qualquer mudanca."),
        ("She noticed the problem before it became serious.", "Ela percebeu o problema antes que ficasse serio.", "Ela criou o problema de proposito.", "Ela nunca viu o problema.", "O problema desapareceu sozinho."),
        ("The final opinion is hopeful but realistic.", "A opiniao final e esperancosa, mas realista.", "A opiniao final e agressiva.", "A opiniao final e confusa e falsa.", "Nao existe opiniao no texto."),
    ],
    "b2": [
        ("The writer compares two approaches before suggesting a reliable strategy.", "O autor compara duas abordagens antes de sugerir uma estrategia confiavel.", "O autor evita qualquer comparacao.", "O autor descreve apenas uma cor.", "O autor rejeita toda estrategia."),
        ("The consequence matters because it changes how the team responds.", "A consequencia importa porque muda como o time responde.", "A consequencia nao afeta ninguem.", "A equipe responde antes do problema.", "A consequencia e apenas decorativa."),
        ("The evidence is limited; however, it still supports the main idea.", "A evidencia e limitada; no entanto, ainda apoia a ideia principal.", "A evidencia prova o oposto totalmente.", "Nao existe ideia principal.", "A evidencia e sobre outro assunto."),
        ("The challenge creates tension between speed and quality.", "O desafio cria tensao entre velocidade e qualidade.", "O desafio remove todas as escolhas.", "A qualidade nunca e mencionada.", "A velocidade nao tem papel nenhum."),
        ("The impact of the choice becomes clearer later.", "O impacto da escolha fica mais claro depois.", "O impacto nunca aparece.", "A escolha e esquecida antes do inicio.", "Tudo fica menos claro sem motivo."),
        ("The pattern suggests a trade-off, not a perfect answer.", "O padrao sugere uma compensacao, nao uma resposta perfeita.", "O padrao oferece uma solucao magica.", "Nao ha nenhum padrao.", "A resposta perfeita aparece imediatamente."),
        ("The reader is invited to question an easy assumption.", "O leitor e convidado a questionar uma suposicao facil.", "O leitor deve aceitar tudo sem pensar.", "A suposicao nao existe.", "O texto manda parar a leitura."),
    ],
    "c1": [
        ("The passage reframes an ordinary event by emphasizing its underlying constraint.", "A passagem reformula um evento comum ao enfatizar sua restricao subjacente.", "A passagem remove qualquer restricao.", "O evento e tratado como irrelevante.", "A passagem fala apenas de clima."),
        ("The insight depends on a subtle shift in perspective.", "A percepcao depende de uma mudanca sutil de perspectiva.", "A percepcao depende de sorte pura.", "A perspectiva permanece identica.", "Nao ha mudanca no texto."),
        ("The argument remains viable because it acknowledges competing priorities.", "O argumento continua viavel porque reconhece prioridades concorrentes.", "O argumento ignora todas as prioridades.", "A viabilidade depende de uma unica palavra.", "O argumento nao tem estrutura."),
        ("The text sustains tension without turning it into a simple conflict.", "O texto sustenta tensao sem transforma-la em conflito simples.", "O texto elimina toda tensao.", "A tensao vira uma piada sem sentido.", "O conflito e explicado por numeros."),
        ("The language is precise enough to suggest hesitation rather than certainty.", "A linguagem e precisa o bastante para sugerir hesitacao, nao certeza.", "A linguagem mostra certeza absoluta.", "A hesitacao e impossivel.", "A precisao nao aparece."),
        ("The conclusion reinforces the theme without repeating it directly.", "A conclusao reforca o tema sem repeti-lo diretamente.", "A conclusao repete cada frase.", "A conclusao muda de assunto.", "Nao ha tema no texto."),
        ("The reader must infer motive from context.", "O leitor deve inferir motivo pelo contexto.", "O motivo e traduzido palavra por palavra.", "O contexto nao ajuda em nada.", "O leitor nao precisa interpretar."),
    ],
    "c2": [
        ("The passage treats ambiguity as a productive force rather than a flaw.", "A passagem trata a ambiguidade como forca produtiva, nao como falha.", "A passagem elimina toda ambiguidade.", "A ambiguidade e chamada de erro gramatical.", "A ambiguidade nao tem funcao."),
        ("Its coherence emerges through friction between competing interpretations.", "A coerencia surge pelo atrito entre interpretacoes concorrentes.", "A coerencia vem de uma unica resposta simples.", "As interpretacoes nunca competem.", "O atrito e fisico e literal."),
        ("The implication is deliberately provisional.", "A implicacao e deliberadamente provisoria.", "A implicacao e definitiva desde o inicio.", "Nao existe implicacao.", "A implicacao e acidental."),
        ("The writer tempers zeal with meticulous scrutiny.", "O autor modera entusiasmo com analise meticulosa.", "O autor evita qualquer analise.", "O entusiasmo domina tudo sem limite.", "A analise e descuidada."),
        ("The final sentence reconciles resilience with uncertainty.", "A frase final reconcilia resiliencia com incerteza.", "A frase final rejeita resiliencia.", "A incerteza desaparece sem motivo.", "A frase final fala de outro tema."),
        ("The text asks the reader to discern a threshold rather than a rule.", "O texto pede que o leitor perceba um limiar, nao uma regra.", "O texto oferece uma regra fixa.", "O limiar e irrelevante.", "O leitor nao precisa discernir nada."),
        ("The style unfolds through implication, not explanation alone.", "O estilo se desdobra por implicacao, nao apenas por explicacao.", "O estilo depende so de definicoes.", "Nao ha implicacao no estilo.", "A explicacao desaparece totalmente."),
    ],
}


class Command(BaseCommand):
    help = "Create leveled texts, vocabulary, quizzes, placement quizzes, and themed SVG illustrations."

    def add_arguments(self, parser):
        parser.add_argument("--per-category", type=int, default=10)

    def handle(self, *args, **options):
        per_category = options["per_category"]
        levels = list(Level.objects.order_by("order"))
        categories = list(Category.objects.filter(is_active=True).order_by("slug"))
        characters = list(Character.objects.filter(is_active=True).order_by("name"))

        if not levels or not categories:
            self.stdout.write(self.style.WARNING("Run seed_initial_data first."))
            return

        self.seed_placement_quizzes(levels)

        total = len(levels) * len(categories) * per_category
        self.stdout.write(f"Creating or updating {total} leveled texts...")

        created_count = 0
        updated_count = 0
        for level in levels:
            for category in categories:
                context = CATEGORY_CONTEXT.get(category.slug, ("Lia", "room", "friend", "idea"))
                for index in range(1, per_category + 1):
                    topic = TOPICS[(index - 1) % len(TOPICS)]
                    character = None
                    if category.slug == "hqs" and characters:
                        character = characters[(index - 1) % len(characters)]

                    title = self.build_title(level, category, topic, character)
                    slug = slugify(f"{level.slug}-{category.slug}-{index:02d}-{topic[0]}")
                    story = self.build_story(level, category, topic, context, character)
                    story = enforce_level_word_limits(
                        story,
                        level.slug,
                        {
                            "subject": character.name if character else context[0],
                            "place_word": topic[1],
                            "object_word": topic[2],
                            "helper": context[2],
                            "value": context[3],
                        },
                    )
                    word_count = count_words(story)
                    text, created = Text.objects.update_or_create(
                        slug=slug,
                        defaults={
                            "title": title,
                            "summary_pt": self.summary_for(level, category, topic),
                            "content_en": story,
                            "level": level,
                            "category": category,
                            "character": character,
                            "word_count": word_count,
                            "estimated_reading_time": max(1, round(word_count / 170)),
                            "image_canvas_width": 500,
                            "image_canvas_height": 500,
                            "status": "published",
                            "published_at": timezone.now(),
                        },
                    )
                    prompt = build_image_prompt(text)
                    if text.image_prompt != prompt:
                        text.image_prompt = prompt
                        text.save(update_fields=["image_prompt"])
                    animation_path = write_text_illustration(text)
                    if text.animation_asset.name != animation_path:
                        text.animation_asset = animation_path
                        text.save(update_fields=["animation_asset"])
                    created_count += int(created)
                    updated_count += int(not created)
                    replace_text_vocabulary(text, max_items=8)
                    self.replace_quiz(text, level, category, topic, context)

        self.stdout.write(self.style.SUCCESS(f"Catalog ready: {created_count} created, {updated_count} updated."))

    def build_title(self, level, category, topic, character):
        if category.slug == "hqs" and character:
            return f"{character.name}: {topic[0]}"
        if level.slug in {"iniciante", "a1"}:
            return topic[0]
        return f"{topic[0]} in {category.name}"

    def summary_for(self, level, category, topic):
        return f"Leitura {level.name} sobre {category.name.lower()}, com frases adequadas ao nivel e tema: {topic[0]}."

    def visual_prompt(self, category, topic, context):
        actor, place, helper, value = context
        return f"Desenho animado de {actor} em {place}, com {topic[2]} e clima de {category.name.lower()}."

    def build_story(self, level, category, topic, context, character=None):
        actor, place, helper, value = context
        title, place_word, object_word = topic
        subject = character.name if character else actor

        builders = {
            "iniciante": self.story_beginner,
            "a1": self.story_a1,
            "a2": self.story_a2,
            "b1": self.story_b1,
            "b2": self.story_b2,
            "c1": self.story_c1,
            "c2": self.story_c2,
        }
        return builders[level.slug](subject, place, helper, value, title, place_word, object_word)

    def story_beginner(self, subject, place, helper, value, title, place_word, object_word):
        sentences = [
            f"{subject} is in the {place_word}.",
            f"The {object_word} is small.",
            f"{subject} can see it.",
            f"A {helper} is near.",
            f"The day is calm.",
            f"{subject} says, \"I can help.\"",
            f"The {object_word} is safe.",
            f"{subject} smiles.",
        ]
        return " ".join(sentences)

    def story_a1(self, subject, place, helper, value, title, place_word, object_word):
        return " ".join(
            [
                f"{subject} goes to the {place_word} after school.",
                f"There is a {object_word} on a small table.",
                f"A {helper} looks at it and asks a question.",
                f"{subject} listens and gives a simple answer.",
                f"The answer is not perfect, but it is clear.",
                f"Now the group can start again.",
                f"{subject} feels happy because the day is easier.",
            ]
        )

    def story_a2(self, subject, place, helper, value, title, place_word, object_word):
        return "\n\n".join(
            [
                " ".join(
                    [
                        f"Last Saturday, {subject} visited the {place_word} with a {helper}.",
                        f"They found a {object_word} near the door.",
                        f"At first, nobody knew why it was there.",
                        f"{subject} read a short note and understood the problem.",
                    ]
                ),
                " ".join(
                    [
                        f"The note asked for a small act of {value}.",
                        f"{subject} and the {helper} made a clear plan.",
                        "They worked slowly, checked each step, and shared the result.",
                        "By the end of the day, the problem felt much smaller.",
                        "The next day, they remembered the lesson and used it again.",
                    ]
                ),
            ]
        )

    def story_b1(self, subject, place, helper, value, title, place_word, object_word):
        return "\n\n".join(
            [
                " ".join(
                    [
                        f"{subject} did not expect the {object_word} to change the afternoon.",
                        f"It was lying in the {place_word}, almost hidden, while people hurried past it.",
                        f"A {helper} noticed that {subject} was curious and offered simple advice.",
                    ]
                ),
                " ".join(
                    [
                        f"Instead of acting quickly, {subject} stopped and thought about the reason for the problem.",
                        f"The choice was small, but it required patience and {value}.",
                        "That made the solution easier to trust.",
                        "The final result was not dramatic; however, it helped everyone understand the situation better.",
                        "The group also learned that a mistake can become useful when people talk about it honestly.",
                        f"For {subject}, the most important part was not being right immediately, but learning how to ask better questions.",
                    ]
                ),
            ]
        )

    def story_b2(self, subject, place, helper, value, title, place_word, object_word):
        return "\n\n".join(
            [
                " ".join(
                    [
                        f"When {subject} found the {object_word} in the {place_word}, the first reaction was to solve the issue immediately.",
                        f"Yet the {helper} suggested a different approach: compare what was urgent with what was actually important.",
                        "That contrast changed the mood of the group.",
                    ]
                ),
                " ".join(
                    [
                        f"The situation became a useful challenge because it connected action with {value}.",
                        "A fast answer would have looked efficient, but it might have ignored the cause of the problem.",
                        "A slower answer gave the group better evidence and a more reliable plan.",
                    ]
                ),
                " ".join(
                    [
                        "By the end, the lesson was clear enough without being simplistic.",
                        f"{subject} learned that good decisions often depend on balance, timing, and the ability to listen before responding.",
                        f"The {helper} agreed, because the best plan protected {value} while still allowing the group to move forward.",
                        "This made the scene feel practical rather than perfect, which is often how real progress appears.",
                    ]
                ),
            ]
        )

    def story_c1(self, subject, place, helper, value, title, place_word, object_word):
        return "\n\n".join(
            [
                " ".join(
                    [
                        f"The {object_word} in the {place_word} seemed ordinary, but {subject} treated it as a clue to a wider pattern.",
                        f"The {helper} initially wanted a direct explanation, while {subject} preferred to examine the quiet details around it.",
                        "That difference in perspective gave the scene its tension.",
                    ]
                ),
                " ".join(
                    [
                        f"What mattered was not the object itself, but the constraint it revealed: people were trying to protect {value} without slowing the day too much.",
                        "The group had to decide which priority deserved attention first.",
                        "A precise answer was possible only after they accepted that the easiest explanation was incomplete.",
                    ]
                ),
                " ".join(
                    [
                        f"In the end, {subject} did not present the solution as a victory.",
                        "The result was more subtle: a shared insight, a better question, and a plan that could be sustained beyond that single moment.",
                        "The text invites the reader to notice how small details can reshape a larger decision.",
                        f"It also suggests that {value} is not a fixed quality, but something people maintain through repeated attention.",
                        "That is why the scene avoids an easy moral and leaves space for reflection.",
                        "The reader is expected to connect motive, context, and consequence rather than translate each sentence in isolation.",
                    ]
                ),
            ]
        )

    def story_c2(self, subject, place, helper, value, title, place_word, object_word):
        return "\n\n".join(
            [
                " ".join(
                    [
                        f"At first glance, the {object_word} in the {place_word} offered {subject} a convenient interpretation.",
                        f"However, the {helper}'s hesitation introduced a productive ambiguity: the scene could be read as a mistake, a warning, or an invitation to revise an assumption.",
                        "That uncertainty gave the moment its force.",
                    ]
                ),
                " ".join(
                    [
                        f"The issue was not whether {value} mattered, but how carefully it could be defended without turning into a rigid rule.",
                        "A superficial response would have resolved the problem quickly and falsely.",
                        "A more meticulous reading exposed the friction between intention, evidence, and consequence.",
                    ]
                ),
                " ".join(
                    [
                        f"{subject} eventually chose a provisional answer, one that preserved coherence without pretending to erase doubt.",
                        "The decision was modest, but its implication was broader: resilience often begins when people learn to act without demanding perfect certainty.",
                        "The final impression is deliberately restrained, asking the reader to discern a threshold rather than accept a simple moral.",
                        f"Through that restraint, the passage turns {value} into a question of judgment rather than a decorative theme.",
                        "It does not reward speed, certainty, or dramatic closure; instead, it values careful interpretation under imperfect conditions.",
                        "The reader must hold several possibilities at once and notice how each one changes the ethical weight of the choice.",
                        "That layered movement is what makes the ending feel complete without becoming closed.",
                    ]
                ),
            ]
        )

    def replace_vocabulary(self, text, level, category, index):
        text.vocabulary.all().delete()
        pool = VOCAB_POOLS[level.slug]
        category_seed = sum(ord(char) for char in category.slug)
        offset = (index * 5 + category_seed) % len(pool)
        selected = [pool[(offset + step * 7) % len(pool)] for step in range(5)]

        VocabularyItem.objects.bulk_create(
            [
                VocabularyItem(
                    text=text,
                    word_en=word,
                    translation_pt=translation,
                    pronunciation_pt=pronunciation,
                    example_en=self.example_for_word(level.slug, word),
                    order=order,
                )
                for order, (word, translation, pronunciation) in enumerate(selected, start=1)
            ]
        )

    def example_for_word(self, level_slug, word):
        if level_slug in {"iniciante", "a1"}:
            return f"I see the {word}."
        if level_slug == "a2":
            return f"The {word} helped the group understand the moment."
        if level_slug == "b1":
            return f"The {word} changed how the character solved the problem."
        if level_slug == "b2":
            return f"The {word} shaped the decision in a clear way."
        return f"The {word} adds nuance to the reader's interpretation."

    def replace_quiz(self, text, level, category, topic, context):
        text.quiz_questions.all().delete()
        actor, place, helper, value = context
        subject = text.character.name if text.character else actor
        object_word = topic[2]
        place_word = topic[1]

        questions = [
            (
                "Who is the main person in the text?",
                subject,
                helper,
                "A stranger with no role",
                "No person appears",
            ),
            (
                "What object is important in the text?",
                f"The {object_word}",
                "A red car",
                "A phone call",
                "A broken window",
            ),
            (
                "Where does the scene connect to?",
                f"The {place_word}",
                "A desert",
                "A hospital",
                "A spaceship",
            ),
            (
                "What does the text show?",
                f"A small moment connected to {value}",
                "A list of unrelated facts",
                "A recipe with no story",
                "A race with no lesson",
            ),
            (
                "What should the reader do?",
                "Read carefully and use context",
                "Skip every new word",
                "Ignore the title",
                "Stop before the ending",
            ),
        ]

        for order, answers in enumerate(questions, start=1):
            question = TextQuizQuestion.objects.create(
                text=text,
                question_text=answers[0],
                order=order,
                is_active=True,
            )
            options = self.rotate_answers(
                [
                    (answers[1], True),
                    (answers[2], False),
                    (answers[3], False),
                    (answers[4], False),
                ],
                sum(ord(char) for char in text.slug) + order,
            )
            TextQuizAnswer.objects.bulk_create(
                [
                    TextQuizAnswer(question=question, answer_text=answer_text, is_correct=is_correct)
                    for answer_text, is_correct in options
                ]
            )

    def seed_placement_quizzes(self, levels):
        PlacementQuizQuestion.objects.all().delete()
        for level in levels:
            for order, row in enumerate(PLACEMENT_DATA[level.slug], start=1):
                question = PlacementQuizQuestion.objects.create(
                    target_level=level,
                    category=None,
                    question_text=f"Leia: \"{row[0]}\". Qual e o melhor sentido?",
                    order=order,
                    is_active=True,
                )
                options = self.rotate_answers(
                    [
                        (row[1], True),
                        (row[2], False),
                        (row[3], False),
                        (row[4], False),
                    ],
                    level.order + order,
                )
                PlacementQuizAnswer.objects.bulk_create(
                    [
                        PlacementQuizAnswer(question=question, answer_text=answer_text, is_correct=is_correct)
                        for answer_text, is_correct in options
                    ]
                )

    def rotate_answers(self, options, seed):
        rotation = seed % len(options)
        return options[rotation:] + options[:rotation]
