import re
from collections import Counter

from .models import VocabularyItem


LEVEL_WORD_LIMITS = {
    "iniciante": (40, 80),
    "a1": (80, 120),
    "a2": (120, 180),
    "b1": (180, 260),
    "b2": (260, 380),
    "c1": (380, 550),
    "c2": (550, 750),
}


LEVEL_STYLE_RULES = {
    "iniciante": "short present-simple sentences, concrete nouns, useful repetition",
    "a1": "daily routines, basic verbs, simple connectors, familiar places",
    "a2": "short narrative, simple past, clear sequence, concrete details",
    "b1": "cause and consequence, simple opinions, varied connectors",
    "b2": "light argument, abstract ideas, balanced longer sentences",
    "c1": "nuance, complex opinions, varied structures, precise vocabulary",
    "c2": "refined prose, inference, ambiguity, advanced vocabulary",
}


HIGH_FREQUENCY_ENGLISH = {
    "a",
    "about",
    "after",
    "again",
    "all",
    "also",
    "am",
    "an",
    "and",
    "are",
    "as",
    "ask",
    "at",
    "be",
    "because",
    "before",
    "big",
    "but",
    "by",
    "can",
    "come",
    "day",
    "did",
    "do",
    "does",
    "each",
    "early",
    "easy",
    "end",
    "even",
    "every",
    "feel",
    "find",
    "first",
    "for",
    "friend",
    "from",
    "get",
    "give",
    "go",
    "good",
    "group",
    "had",
    "has",
    "have",
    "he",
    "help",
    "her",
    "here",
    "him",
    "his",
    "home",
    "how",
    "i",
    "if",
    "in",
    "into",
    "is",
    "it",
    "know",
    "last",
    "learn",
    "like",
    "little",
    "look",
    "made",
    "make",
    "many",
    "me",
    "more",
    "most",
    "new",
    "no",
    "not",
    "now",
    "of",
    "on",
    "one",
    "open",
    "or",
    "other",
    "our",
    "out",
    "people",
    "place",
    "read",
    "right",
    "said",
    "same",
    "school",
    "see",
    "she",
    "short",
    "simple",
    "small",
    "so",
    "some",
    "start",
    "still",
    "take",
    "talk",
    "teacher",
    "text",
    "that",
    "the",
    "their",
    "them",
    "then",
    "there",
    "they",
    "thing",
    "think",
    "this",
    "time",
    "to",
    "today",
    "try",
    "two",
    "up",
    "us",
    "use",
    "very",
    "walk",
    "want",
    "was",
    "way",
    "we",
    "were",
    "what",
    "when",
    "where",
    "which",
    "while",
    "who",
    "why",
    "will",
    "with",
    "work",
    "would",
    "you",
}


TRANSLATION_HINTS = {
    "afternoon": "tarde",
    "america": "America",
    "ambiguity": "ambiguidade",
    "answer": "resposta",
    "aquaman": "Aquaman",
    "arrow": "flecha",
    "assumption": "suposicao",
    "attention": "atencao",
    "band": "banda",
    "balance": "equilibrio",
    "batman": "Batman",
    "become": "tornar-se",
    "believed": "acreditou",
    "black": "preto",
    "calm": "calmo",
    "captain": "capitao",
    "challenge": "desafio",
    "checked": "verificou",
    "choice": "escolha",
    "city": "cidade",
    "clear": "claro",
    "coach": "treinador",
    "coherence": "coerencia",
    "confident": "confiante",
    "consequence": "consequencia",
    "constraint": "restricao",
    "cyborg": "ciborgue",
    "deadpool": "Deadpool",
    "decision": "decisao",
    "deliberately": "deliberadamente",
    "detail": "detalhe",
    "discern": "discernir",
    "doctor": "medico",
    "door": "porta",
    "easier": "mais facil",
    "episode": "episodio",
    "everyone": "todos",
    "evidence": "evidencia",
    "explained": "explicou",
    "explanation": "explicacao",
    "family": "familia",
    "friction": "atrito",
    "green": "verde",
    "habit": "habito",
    "hero": "heroi",
    "hesitation": "hesitacao",
    "house": "casa",
    "impact": "impacto",
    "implication": "implicacao",
    "insight": "percepcao",
    "interpretation": "interpretacao",
    "judgment": "julgamento",
    "kind": "gentil",
    "kitchen": "cozinha",
    "lantern": "lanterna",
    "lesson": "licao",
    "level": "nivel",
    "library": "biblioteca",
    "light": "luz",
    "luna": "Luna",
    "marvel": "Marvel",
    "mattered": "importava",
    "maya": "Maya",
    "meticulous": "meticuloso",
    "motive": "motivo",
    "music": "musica",
    "nature": "natureza",
    "near": "perto",
    "neighbor": "vizinho",
    "nora": "Nora",
    "note": "anotacao",
    "noticed": "percebeu",
    "nuance": "nuance",
    "panther": "pantera",
    "park": "parque",
    "pattern": "padrao",
    "perfect": "perfeito",
    "perspective": "perspectiva",
    "person": "pessoa",
    "plan": "plano",
    "precise": "preciso",
    "practice": "pratica",
    "problem": "problema",
    "productive": "produtivo",
    "provisional": "provisorio",
    "question": "pergunta",
    "reader": "leitor",
    "reliable": "confiavel",
    "remember": "lembrar",
    "remembered": "lembrou",
    "resilience": "resiliencia",
    "restraint": "contencao",
    "revealed": "revelou",
    "robot": "robo",
    "room": "quarto ou sala",
    "safe": "seguro",
    "says": "diz",
    "scene": "cena",
    "scrutiny": "analise minuciosa",
    "sister": "irma",
    "slowly": "lentamente",
    "smile": "sorriso",
    "sofia": "Sofia",
    "song": "cancao",
    "sound": "som",
    "strategy": "estrategia",
    "story": "historia",
    "strange": "estranho",
    "street": "rua",
    "subtle": "sutil",
    "team": "equipe",
    "theo": "Theo",
    "threshold": "limiar",
    "tool": "ferramenta",
    "trade-off": "troca ou compensacao",
    "tree": "arvore",
    "trend": "tendencia",
    "trip": "viagem",
    "tension": "tensao",
    "underlying": "subjacente",
    "understood": "entendeu",
    "without": "sem",
    "word": "palavra",
    "yard": "quintal",
}


PRONUNCIATION_HINTS = {
    "afternoon": "af-ter-NUN",
    "america": "a-ME-ri-ka",
    "answer": "AN-ser",
    "aquaman": "A-kua-man",
    "arrow": "E-rou",
    "attention": "a-TEN-shon",
    "band": "BAND",
    "batman": "BAT-man",
    "become": "bi-KAM",
    "becomes": "bi-KAMZ",
    "believed": "bi-LIVD",
    "black": "BLAK",
    "calm": "KAM",
    "captain": "KAP-ten",
    "checked": "CHEKT",
    "choice": "TCHOIS",
    "city": "SI-ti",
    "clear": "KLIR",
    "coach": "KOUTCH",
    "confident": "KAN-fi-dent",
    "consequence": "KAN-si-kuens",
    "constraint": "kon-STREINT",
    "cyborg": "SAI-borg",
    "deadpool": "DED-pul",
    "decision": "di-SI-jon",
    "deliberately": "di-LI-ber-it-li",
    "detail": "DI-teil",
    "doctor": "DAK-ter",
    "door": "DOR",
    "easier": "I-zi-er",
    "episode": "E-pi-soud",
    "everyone": "EV-ri-uan",
    "evidence": "E-vi-dens",
    "explained": "eks-PLEIND",
    "explanation": "eks-pla-NEI-shon",
    "family": "FE-mi-li",
    "green": "GRIN",
    "habit": "HA-bit",
    "hero": "HI-rou",
    "hesitation": "re-zi-TEI-shon",
    "house": "RAUS",
    "interpretation": "in-ter-pri-TEI-shon",
    "kind": "KAIND",
    "kitchen": "KI-tchen",
    "lantern": "LAN-tern",
    "lesson": "LE-son",
    "level": "LE-vol",
    "library": "LAI-bre-ri",
    "light": "LAIT",
    "luna": "LU-na",
    "marvel": "MAR-vol",
    "mattered": "MA-terd",
    "maya": "MAI-a",
    "music": "MIU-zik",
    "nature": "NEI-tcher",
    "near": "NIR",
    "neighbor": "NEI-bor",
    "nora": "NO-ra",
    "note": "NOUT",
    "noticed": "NOU-tist",
    "panther": "PAN-ter",
    "park": "PARK",
    "perfect": "PER-fekt",
    "person": "PER-son",
    "perspective": "per-SPEK-tiv",
    "plan": "PLAN",
    "practice": "PRAK-tis",
    "problem": "PRA-blem",
    "productive": "pro-DAK-tiv",
    "provisional": "pro-VI-jo-nal",
    "question": "KUES-tchon",
    "reader": "RI-der",
    "reliable": "ri-LAI-a-bol",
    "remember": "ri-MEM-ber",
    "remembered": "ri-MEM-berd",
    "revealed": "ri-VILD",
    "robot": "ROU-bot",
    "room": "RUM",
    "safe": "SEIF",
    "says": "SEZ",
    "scene": "SIN",
    "sister": "SIS-ter",
    "slowly": "SLOU-li",
    "smile": "SMAIL",
    "sofia": "so-FI-a",
    "song": "SONG",
    "sound": "SAUND",
    "story": "STO-ri",
    "strange": "STREINDJ",
    "street": "STRIT",
    "team": "TIM",
    "theo": "TI-ou",
    "tool": "TUL",
    "trade-off": "TREID-of",
    "tree": "TRI",
    "trend": "TREND",
    "trip": "TRIP",
    "understood": "an-der-STUD",
    "without": "ui-DAUT",
    "word": "UORD",
    "yard": "IARD",
}


POS_MAP = {
    "NOUN": "noun",
    "PROPN": "noun",
    "VERB": "verb",
    "ADJ": "adjective",
    "NN": "noun",
    "NNS": "noun",
    "NNP": "noun",
    "NNPS": "noun",
    "VB": "verb",
    "VBD": "verb",
    "VBG": "verb",
    "VBN": "verb",
    "VBP": "verb",
    "VBZ": "verb",
    "JJ": "adjective",
    "JJR": "adjective",
    "JJS": "adjective",
}


TOKEN_RE = re.compile(r"[A-Za-z][A-Za-z'-]{2,}")
SENTENCE_RE = re.compile(r"[^.!?]+[.!?]")


def load_frequency_words(path=None):
    if not path:
        return set(HIGH_FREQUENCY_ENGLISH)

    with open(path, encoding="utf-8") as frequency_file:
        words = {
            line.strip().lower()
            for line in frequency_file
            if line.strip() and not line.strip().startswith("#")
        }
    return words | HIGH_FREQUENCY_ENGLISH


def extract_vocabulary_candidates(content, high_frequency_words=None, max_items=8):
    high_frequency_words = high_frequency_words or HIGH_FREQUENCY_ENGLISH
    tokens = _spacy_tokens(content) or _nltk_tokens(content) or _heuristic_tokens(content)
    counts = Counter(token["lemma"] for token in tokens)
    selected = {}

    for position, token in enumerate(tokens):
        lemma = token["lemma"].lower().strip("'")
        if not _is_candidate_lemma(lemma, high_frequency_words):
            continue
        existing = selected.get(lemma)
        score = (counts[lemma] * 10) + len(lemma) + _pos_score(token["part_of_speech"])
        if existing is None or score > existing["score"]:
            selected[lemma] = {
                "word": token["word"],
                "lemma": lemma,
                "part_of_speech": token["part_of_speech"],
                "position": position,
                "score": score,
            }

    return sorted(selected.values(), key=lambda item: (-item["score"], item["position"]))[:max_items]


def replace_text_vocabulary(text, max_items=8, frequency_words=None, source="dynamic_nlp"):
    candidates = extract_vocabulary_candidates(text.content_en, frequency_words, max_items=max_items)
    previous_translations = _translation_lookup()

    text.vocabulary.all().delete()
    items = []
    for order, candidate in enumerate(candidates, start=1):
        lemma = candidate["lemma"]
        display_word = candidate["word"].strip("'")
        items.append(
            VocabularyItem(
                text=text,
                word_en=display_word,
                lemma_en=lemma,
                part_of_speech=candidate["part_of_speech"],
                translation_pt=translation_for(lemma, previous_translations),
                pronunciation_pt=simplified_pronunciation(display_word),
                example_en=example_sentence_for(text.content_en, display_word),
                source=source,
                frequency_rank=None,
                order=order,
            )
        )

    VocabularyItem.objects.bulk_create(items)
    return items


def build_image_prompt(text):
    scene = _scene_from_text(text.title, text.summary_pt, text.content_en)
    level_style = LEVEL_STYLE_RULES.get(text.level.slug, "leveled English reading")
    return (
        "Estilo desenho cartoon educacional, canvas quadrado 500x500px, fundo transparente, "
        "paleta Lecto com azul profundo #1C4259, dourado claro #D9B97E e caramelo #BF9663, "
        f"retratando {scene}. Categoria {text.category.name}. Nivel {text.level.name}. "
        f"Clareza visual para estudantes brasileiros; evitar texto dentro da imagem; {level_style}."
    )


def enforce_level_word_limits(story, level_slug, context):
    min_words, max_words = LEVEL_WORD_LIMITS.get(level_slug, (40, 120))
    story = _normalize_story(story)
    additions = _level_expansion_sentences(level_slug, context)
    index = 0

    while word_count(story) < min_words:
        next_sentence = additions[index % len(additions)]
        candidate = _normalize_story(f"{story} {next_sentence}")
        if word_count(candidate) <= max_words:
            story = candidate
        else:
            story = _append_needed_words(story, min_words, max_words)
        index += 1

    if word_count(story) > max_words:
        story = trim_to_word_limit(story, max_words)

    return story


def word_count(value):
    return len(TOKEN_RE.findall(value or ""))


def trim_to_word_limit(story, max_words):
    sentences = SENTENCE_RE.findall(story)
    kept = []
    for sentence in sentences:
        candidate = " ".join(kept + [sentence.strip()])
        if word_count(candidate) > max_words:
            break
        kept.append(sentence.strip())
    if kept:
        return _normalize_story(" ".join(kept))

    words = TOKEN_RE.findall(story)
    return " ".join(words[:max_words]) + "."


def _spacy_tokens(content):
    try:
        import spacy

        nlp = spacy.load("en_core_web_sm", disable=["ner"])
    except Exception:
        return None

    parsed = nlp(content)
    tokens = []
    for token in parsed:
        part_of_speech = POS_MAP.get(token.pos_)
        if part_of_speech and token.is_alpha and not token.is_stop:
            tokens.append(
                {
                    "word": token.text,
                    "lemma": token.lemma_.lower(),
                    "part_of_speech": part_of_speech,
                }
            )
    return tokens


def _nltk_tokens(content):
    try:
        import nltk

        words = nltk.word_tokenize(content)
        tagged_words = nltk.pos_tag(words)
    except Exception:
        return None

    tokens = []
    for word, tag in tagged_words:
        part_of_speech = POS_MAP.get(tag)
        if part_of_speech and TOKEN_RE.fullmatch(word):
            tokens.append(
                {
                    "word": word,
                    "lemma": _simple_lemma(word, part_of_speech),
                    "part_of_speech": part_of_speech,
                }
            )
    return tokens


def _heuristic_tokens(content):
    tokens = []
    for word in TOKEN_RE.findall(content):
        lemma = _simple_lemma(word, "")
        part_of_speech = _guess_part_of_speech(lemma)
        if part_of_speech:
            tokens.append({"word": word, "lemma": lemma, "part_of_speech": part_of_speech})
    return tokens


def _simple_lemma(word, part_of_speech):
    lemma = word.lower().strip("'")
    irregular = {
        "went": "go",
        "gone": "go",
        "made": "make",
        "thought": "think",
        "found": "find",
        "people": "person",
        "children": "child",
    }
    if lemma in irregular:
        return irregular[lemma]
    if part_of_speech == "verb" and lemma.endswith("ing") and len(lemma) > 5:
        return lemma[:-3]
    if part_of_speech == "verb" and lemma.endswith("ed") and len(lemma) > 4:
        return lemma[:-2]
    if lemma.endswith("ies") and len(lemma) > 5:
        return lemma[:-3] + "y"
    if lemma.endswith("s") and len(lemma) > 4 and not lemma.endswith("ss"):
        return lemma[:-1]
    return lemma


def _guess_part_of_speech(lemma):
    if lemma in HIGH_FREQUENCY_ENGLISH or len(lemma) < 4:
        return None
    if lemma.endswith(("ous", "ful", "ive", "less", "able", "ible", "al", "ic")):
        return "adjective"
    if lemma.endswith(("ate", "ify", "ise", "ize", "en")):
        return "verb"
    return "noun"


def _is_candidate_lemma(lemma, high_frequency_words):
    return (
        lemma
        and len(lemma) >= 4
        and lemma not in high_frequency_words
        and not lemma.isdigit()
        and "'" not in lemma
    )


def _pos_score(part_of_speech):
    return {"noun": 3, "verb": 2, "adjective": 2}.get(part_of_speech, 0)


def _translation_lookup():
    lookup = dict(TRANSLATION_HINTS)
    rows = (
        VocabularyItem.objects.exclude(translation_pt="")
        .exclude(translation_pt__iexact="Traducao pendente")
        .values_list("lemma_en", "word_en", "translation_pt")
        .distinct()
    )
    for lemma, word, translation in rows:
        lookup.setdefault((lemma or word).lower(), translation)
    return lookup


def translation_for(lemma, previous_translations):
    normalized = (lemma or "").lower()
    return previous_translations.get(normalized) or TRANSLATION_HINTS.get(normalized) or normalized.replace("-", " ")


def simplified_pronunciation(word):
    normalized = (word or "").lower().strip()
    if normalized in PRONUNCIATION_HINTS:
        return PRONUNCIATION_HINTS[normalized]

    value = word.lower()
    replacements = [
        ("tion", "shon"),
        ("sion", "zhon"),
        ("th", "th"),
        ("ph", "f"),
        ("ough", "of"),
        ("ai", "ei"),
        ("ay", "ei"),
        ("ee", "ii"),
        ("ea", "ii"),
        ("oo", "u"),
        ("ow", "au"),
    ]
    for old, new in replacements:
        value = value.replace(old, new)
    return value


def example_sentence_for(content, word):
    pattern = re.compile(rf"[^.!?]*\b{re.escape(word)}\b[^.!?]*[.!?]", re.IGNORECASE)
    match = pattern.search(content)
    if match:
        sentence = " ".join(match.group(0).split())
        return sentence[:237] + "..." if len(sentence) > 240 else sentence
    return f"The word {word} appears in this text."


def _scene_from_text(title, summary, content):
    joined = " ".join([title or "", summary or "", content or ""]).lower()
    scene_words = []
    for word in TOKEN_RE.findall(joined):
        lemma = _simple_lemma(word, "")
        if lemma not in HIGH_FREQUENCY_ENGLISH and len(lemma) > 3:
            scene_words.append(lemma)
        if len(scene_words) == 8:
            break
    scene = ", ".join(dict.fromkeys(scene_words))
    if not scene:
        scene = title
    return f"uma cena sobre {title}, com elementos visuais de {scene}"


def _normalize_story(story):
    paragraphs = [" ".join(part.split()) for part in (story or "").split("\n\n") if part.strip()]
    return "\n\n".join(paragraphs)


def _level_expansion_sentences(level_slug, context):
    subject = context["subject"]
    helper = context["helper"]
    value = context["value"]
    object_word = context["object_word"]
    place_word = context["place_word"]

    banks = {
        "iniciante": [
            f"{subject} looks at the {object_word} again.",
            f"The {helper} is kind and calm.",
            f"The {place_word} feels safe today.",
            f"{subject} can read one more word.",
        ],
        "a1": [
            f"{subject} walks slowly around the {place_word} and checks the {object_word}.",
            f"The {helper} writes one clear note, so the next step is easy.",
            f"They talk about {value} and choose a simple plan for the afternoon.",
            f"At home, {subject} remembers the moment and feels ready to read again.",
        ],
        "a2": [
            f"After a few minutes, {subject} compared the first idea with a second, safer choice.",
            f"The {helper} explained that the {object_word} was useful because it made the plan visible.",
            f"They finished the work before evening, but they still checked the details twice.",
            f"Later, the same lesson helped {subject} solve a different problem with less stress.",
        ],
        "b1": [
            f"The {helper} believed the moment mattered because it showed how {value} can guide a small decision.",
            f"{subject} noticed that the {object_word} was not just an object; it changed how people understood the place.",
            f"The group avoided a quick answer and chose a slower explanation that everyone could trust.",
            f"That choice made the ending more useful, because it connected effort with a practical result.",
        ],
        "b2": [
            f"The scene also revealed a trade-off: speed made the group confident, while patience made the answer more reliable.",
            f"By comparing those options, {subject} learned that {value} depends on context, not on a single rule.",
            f"The {helper} kept asking for evidence, and that habit prevented the discussion from becoming too simple.",
            f"Nothing about the result was perfect, yet the process gave the group a strategy they could repeat.",
        ],
        "c1": [
            f"The apparent simplicity of the {object_word} became important because it exposed an underlying constraint in the {place_word}.",
            f"{subject} had to maintain attention to detail while accepting that the easiest explanation remained incomplete.",
            f"The {helper} eventually recognized that {value} was less a final answer than a practice of repeated judgment.",
            f"This shift in perspective gave the episode a layered quality, allowing the reader to infer motive from context.",
            f"Instead of closing the scene with certainty, the narrative preserves tension and asks the reader to notice quiet consequences.",
        ],
        "c2": [
            f"The {object_word} therefore functions as a deliberately modest pressure point, making the {place_word} feel ethically charged without becoming theatrical.",
            f"{subject} resists the comfort of a single interpretation, because each possible explanation changes the responsibility attached to {value}.",
            f"The {helper}'s hesitation is not a weakness in the scene; it is the mechanism through which ambiguity becomes productive.",
            f"What appears practical at first slowly becomes speculative, inviting the reader to reconcile evidence with provisional judgment.",
            f"The passage rewards scrutiny over certainty, suggesting that resilience may begin in the willingness to act under incomplete knowledge.",
            f"That restraint keeps the ending coherent, while still leaving enough friction for a more advanced reader to examine.",
            f"Even the quiet details matter, because they temper enthusiasm with a precise awareness of consequence.",
        ],
    }
    return banks.get(level_slug, banks["a2"])


def _append_needed_words(story, min_words, max_words):
    bridges = [
        "The final detail keeps the lesson clear.",
        "This small choice helps the reader understand the scene.",
        "The moment remains focused and easy to follow.",
    ]
    for bridge in bridges:
        candidate = _normalize_story(f"{story} {bridge}")
        if word_count(candidate) <= max_words:
            return candidate
    return trim_to_word_limit(story, max_words)
