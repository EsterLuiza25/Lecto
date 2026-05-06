import re
from collections import Counter


PROMPT_PREFIX = "Digital art, 2D cartoon style, clean lines, high quality"
LECTO_PALETTE = "using the palette #1C4259 and #D9B97E"
TEXT_PROMPT_SUFFIX = "featuring the book-mascot Alexandrinho, using the palette #1C4259 and #D9B97E, no text, no copyright infringement"


STOPWORDS = {
    "about",
    "after",
    "again",
    "also",
    "because",
    "before",
    "could",
    "every",
    "first",
    "from",
    "have",
    "into",
    "more",
    "near",
    "only",
    "people",
    "place",
    "same",
    "scene",
    "small",
    "story",
    "that",
    "their",
    "there",
    "these",
    "they",
    "this",
    "through",
    "today",
    "under",
    "until",
    "with",
    "without",
    "would",
}


HERO_VISUAL_DESCRIPTIONS = {
    "spider-man": "an agile young city hero with acrobatic movement, web-inspired gear, and expressive mask-like eyes",
    "iron-man": "a hero with sleek technological armor, glowing energy details, and a careful inventor posture",
    "captain-america": "a disciplined patriotic-style hero with a protective round shield motif and calm leadership",
    "thor": "a mythic thunder warrior with a heavy hammer-like tool, flowing cape shape, and storm energy",
    "hulk": "a very strong green-toned gentle giant with broad shoulders and controlled emotional tension",
    "black-panther": "a noble agile guardian in a dark feline-inspired suit silhouette with elegant gold accents",
    "doctor-strange": "a mystical scholar hero with a dramatic cloak shape, floating symbols, and focused hand gestures",
    "wolverine": "a rugged wilderness hero with sharp claw-like gear, worn jacket shapes, and intense posture",
    "deadpool": "a comic antihero with red-and-black playful gear, expressive body language, and mischievous humor",
    "captain-marvel": "a cosmic flying hero with star-like energy, luminous movement, and confident posture",
    "superman": "a hopeful flying hero with strong shoulders, cape silhouette, and warm protective expression",
    "batman": "a nocturnal detective hero with dark cape silhouette, pointed cowl-like shape, and investigative focus",
    "wonder-woman": "a brave warrior diplomat with elegant armor-inspired shapes, lasso-like golden detail, and calm strength",
    "the-flash": "a lightning-fast runner hero with streamlined suit shapes, motion streaks, and energetic pose",
    "aquaman": "an ocean guardian hero with aquatic armor shapes, wave motifs, and a trident-like silhouette",
    "green-lantern": "a willpower-based space hero with glowing green construct shapes and focused imagination",
    "green-arrow": "a precise archer hero with hooded silhouette, bow-inspired gear, and careful aim",
    "cyborg": "a human-machine hero with modular cybernetic armor, glowing interface details, and thoughtful expression",
    "harley-quinn": "a playful acrobatic trickster figure with bold contrasting colors and expressive carnival energy",
    "joker": "a theatrical trickster figure with purple-green palette hints, dramatic grin energy, and chaotic stage presence",
}


COPYRIGHT_NAMES = {
    "Spider-Man",
    "Iron Man",
    "Captain America",
    "Thor",
    "Hulk",
    "Black Panther",
    "Doctor Strange",
    "Wolverine",
    "Deadpool",
    "Captain Marvel",
    "Superman",
    "Batman",
    "Wonder Woman",
    "The Flash",
    "Aquaman",
    "Green Lantern",
    "Green Arrow",
    "Cyborg",
    "Harley Quinn",
    "Joker",
}


TOKEN_RE = re.compile(r"[A-Za-z][A-Za-z'-]{2,}")
SENTENCE_RE = re.compile(r"[^.!?]+[.!?]")


def build_text_image_prompt(text):
    scene = extract_scene(text)
    if text.category.slug == "hqs" and text.character:
        hero = HERO_VISUAL_DESCRIPTIONS.get(text.character.slug, "an original comic-book-inspired hero")
        scene = remove_copyright_names(scene)
        scene = f"{scene}, featuring {hero}, original transformative design with no logos and no copied costume"

    return f"{PROMPT_PREFIX}, {scene}, {TEXT_PROMPT_SUFFIX}"


def extract_scene(text):
    source_text = f"{text.title} {text.summary_pt} {text.content_en}"
    title_scene = clean_visual_text(text.title)
    if getattr(text.category, "slug", "") == "hqs":
        source_text = remove_copyright_names(source_text)
        title_scene = remove_copyright_names(title_scene)

    sentence = best_content_sentence(text.content_en)
    if getattr(text.category, "slug", "") == "hqs":
        sentence = remove_copyright_names(sentence)
    keywords = keyword_phrase(source_text, limit=5)
    level_name = getattr(text.level, "name", "")
    category_name = getattr(text.category, "name", "")

    pieces = [
        f"a square educational illustration for the story '{title_scene}'",
        f"showing {sentence}",
    ]
    if keywords:
        pieces.append(f"visual motifs: {keywords}")
    if category_name:
        pieces.append(f"category mood: {clean_visual_text(category_name)}")
    if level_name:
        pieces.append(f"clear composition for {clean_visual_text(level_name)} English readers")
    return ", ".join(pieces)


def best_content_sentence(content):
    sentences = [
        clean_visual_text(match.group(0))
        for match in SENTENCE_RE.finditer(content or "")
        if 35 <= len(match.group(0).strip()) <= 190
    ]
    if not sentences:
        sentences = [clean_visual_text((content or "")[:180])]
    if not sentences:
        return "a friendly learning scene with a clear object and a focused reader"

    scored = []
    for sentence in sentences[:18]:
        lower = sentence.lower()
        score = 0
        score += 3 if any(word in lower for word in ("found", "noticed", "looked", "opened", "held", "used")) else 0
        score += 2 if any(word in lower for word in ("door", "map", "book", "letter", "city", "room", "garden", "street")) else 0
        score += min(len(TOKEN_RE.findall(sentence)), 28)
        scored.append((score, sentence))
    return max(scored, key=lambda item: item[0])[1]


def keyword_phrase(value, limit=5):
    words = []
    for token in TOKEN_RE.findall(value or ""):
        word = token.lower().strip("'")
        if len(word) < 4 or word in STOPWORDS:
            continue
        words.append(word)
    if not words:
        return ""
    counts = Counter(words)
    return ", ".join(word for word, _ in counts.most_common(limit))


def clean_visual_text(value):
    value = " ".join((value or "").replace("\n", " ").split())
    value = value.replace('"', "'")
    return value[:260].rstrip()


def remove_copyright_names(value):
    cleaned = value
    for name in COPYRIGHT_NAMES:
        cleaned = re.sub(re.escape(name), "the original hero", cleaned, flags=re.IGNORECASE)
    return " ".join(cleaned.split())


def build_avatar_asset_prompt(option):
    description = avatar_layer_description(option)
    return (
        "Digital art, 2D cartoon modular avatar layer, clean lines, high quality, "
        f"{description}, featuring Lecto visual identity, using the palette #1C4259 and #D9B97E, "
        "transparent background, no text, no copyright infringement, square PNG, centered 500x500 canvas, "
        "consistent proportions for CSS layer stacking, soft depth, friendly educational style"
    )


def avatar_layer_description(option):
    name = clean_visual_text(option.name).lower()
    option_type = option.option_type
    layer = {
        "base_body": "base head, neck and shoulders silhouette for a friendly humanoid student avatar",
        "body_style": "body shape layer with balanced neck and shoulders for a humanoid student avatar",
        "hair_style": "hair layer that fits above the head without covering the eyes",
        "eyes": "eye expression layer aligned to the face with warm readable emotion",
        "accessory": "small accessory layer aligned to the head or shoulders",
        "outfit": "outfit layer for the torso with clean school-friendly design",
        "preset": "complete friendly student avatar preset",
    }.get(option_type, "modular avatar layer")

    traits = []
    if "curto" in name or "short" in name:
        traits.append("short shape")
    if "longo" in name or "long" in name:
        traits.append("long flowing shape")
    if "cacheado" in name or "curly" in name:
        traits.append("curly rounded volume")
    if "oculos" in name or "glasses" in name:
        traits.append("simple glasses")
    if "lenco" in name or "scarf" in name:
        traits.append("soft cloth detail")
    if "dour" in name:
        traits.append("gold accent")
    if "azul" in name:
        traits.append("deep blue accent")
    if "masculino" in name:
        traits.append("masculine presentation")
    if "feminino" in name:
        traits.append("feminine presentation")

    trait_text = ", ".join(traits) if traits else f"based on the option name '{clean_visual_text(option.name)}'"
    return f"{layer}, {trait_text}, layer type {option_type}"
