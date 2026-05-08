from hashlib import sha1
from html import escape
from pathlib import Path

from django.conf import settings

from .content_pipeline import build_image_prompt


CATEGORY_MOTIFS = {
    "anime": "anime",
    "contos": "story",
    "cotidiano": "everyday",
    "cultura-pop": "pop",
    "games": "game",
    "hqs": "hero",
    "meio-ambiente": "nature",
    "musica": "music",
    "saude-e-bem-estar": "wellness",
    "series": "tv",
    "tecnologia": "tech",
    "viagens": "travel",
}


KEYWORD_MOTIFS = [
    ("travel", ("trip", "road", "train", "bus", "map", "station", "bridge", "beach")),
    ("food", ("cake", "tea", "kitchen", "shop")),
    ("music", ("song", "voice", "stage", "music", "band")),
    ("nature", ("park", "tree", "river", "water", "rain", "garden", "kite")),
    ("tech", ("robot", "screen", "game", "tool", "lab")),
    ("mystery", ("key", "box", "door", "clue", "hidden")),
    ("school", ("book", "bag", "note", "page", "desk", "class", "idea", "photo")),
]


PALETTES = {
    "travel": ("#1c4259", "#2f8f8b", "#d9b97e", "#f6f4e8", "#d86f45"),
    "food": ("#7a5436", "#d86f45", "#d9b97e", "#fff6e8", "#2f8f8b"),
    "music": ("#26314f", "#6f83b7", "#d9b97e", "#f6f1f8", "#d86f45"),
    "nature": ("#1f4d3b", "#3d7c5f", "#d9b97e", "#eef7ec", "#2f8f8b"),
    "tech": ("#172b36", "#2f8f8b", "#8fc9c5", "#eef7f6", "#d9b97e"),
    "science": ("#17384d", "#2f8f8b", "#d9b97e", "#eef6fa", "#6f83b7"),
    "sport": ("#224239", "#3d7c5f", "#d9b97e", "#eef7ec", "#d86f45"),
    "hero": ("#1c4259", "#d86f45", "#d9b97e", "#eef2f5", "#2f8f8b"),
    "movie": ("#202633", "#bf9663", "#d9b97e", "#f6f2ec", "#6f83b7"),
    "game": ("#1f2f47", "#6f83b7", "#2f8f8b", "#f0f3fb", "#d86f45"),
    "mystery": ("#25314f", "#7a5436", "#d9b97e", "#f4f0e6", "#2f8f8b"),
    "school": ("#1c4259", "#bf9663", "#d9b97e", "#f7f4ea", "#2f8f8b"),
    "news": ("#172b36", "#d86f45", "#d9b97e", "#f8f8f2", "#2f8f8b"),
    "wellness": ("#275444", "#3d7c5f", "#d9b97e", "#f0f7ef", "#d86f45"),
    "anime": ("#26314f", "#6f83b7", "#d9b97e", "#f7f2fb", "#d86f45"),
    "pop": ("#1c4259", "#d86f45", "#d9b97e", "#fff4ee", "#6f83b7"),
    "tv": ("#202633", "#2f8f8b", "#d9b97e", "#f3f6f5", "#d86f45"),
    "history": ("#704f34", "#bf9663", "#d9b97e", "#f8f1df", "#1c4259"),
    "portrait": ("#1c4259", "#bf9663", "#d9b97e", "#f7f4ea", "#d86f45"),
    "story": ("#273f39", "#3d7c5f", "#d9b97e", "#f2f6ed", "#bf9663"),
    "everyday": ("#1c4259", "#2f8f8b", "#d9b97e", "#f6f4e8", "#bf9663"),
    "weather": ("#17384d", "#8fc9c5", "#d9b97e", "#eef6fa", "#6f83b7"),
}


def write_text_illustration(text):
    prompt = text.image_prompt or build_image_prompt(text)
    return write_story_illustration(
        slug=text.slug,
        title=text.title,
        level_name=text.level.name,
        category_slug=text.category.slug,
        category_name=text.category.name,
        summary=text.summary_pt,
        content=text.content_en,
        prompt=prompt,
    )


def build_text_illustration_svg(text):
    prompt = text.image_prompt or build_image_prompt(text)
    return build_story_illustration_svg(
        slug=text.slug,
        title=text.title,
        level_name=text.level.name,
        category_slug=text.category.slug,
        category_name=text.category.name,
        summary=text.summary_pt,
        content=text.content_en,
        prompt=prompt,
    )


def write_story_illustration(slug, title, level_name, category_slug, category_name, summary="", content="", prompt=""):
    asset_dir = Path(settings.MEDIA_ROOT) / "texts" / "illustrations"
    asset_dir.mkdir(parents=True, exist_ok=True)

    relative_path = f"texts/illustrations/{slug}.svg"
    full_path = Path(settings.MEDIA_ROOT) / relative_path
    svg = build_story_illustration_svg(
        slug=slug,
        title=title,
        level_name=level_name,
        category_slug=category_slug,
        category_name=category_name,
        summary=summary,
        content=content,
        prompt=prompt,
    )
    full_path.write_text(svg, encoding="utf-8")
    return relative_path


def build_story_illustration_svg(slug, title, level_name, category_slug, category_name, summary="", content="", prompt=""):
    seed = _seed(slug)
    motif = _infer_motif(category_slug, title, summary, content)
    object_motif = _infer_keyword_motif(f"{title} {summary} {content}")
    palette = PALETTES.get(motif, PALETTES["everyday"])
    primary, secondary, warm, paper, accent = palette

    safe_title = escape(_shorten(title, 46))
    safe_category = escape(f"{category_name} / {level_name}")
    safe_prompt = escape(prompt or f"{title} - {summary}")
    object_badge = _object_badge(object_motif or motif, primary, secondary, warm, accent, seed)

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 500 500" width="500" height="500" role="img" aria-label="{safe_title}">
<title>{safe_title}</title>
<desc>{safe_prompt}</desc>
<g transform="translate(0 132) scale(0.5556)">
{_background(motif, primary, secondary, warm, accent, seed)}
{_motif(motif, primary, secondary, warm, paper, accent, seed)}
{object_badge}
<g>
<rect x="42" y="34" width="360" height="78" rx="18" fill="#ffffff" opacity=".9"/>
<text x="64" y="65" font-family="Arial, Helvetica, sans-serif" font-size="20" font-weight="800" fill="{primary}">{safe_category}</text>
<text x="64" y="94" font-family="Arial, Helvetica, sans-serif" font-size="18" font-weight="700" fill="{primary}" opacity=".78">{safe_title}</text>
</g>
</g>
</svg>"""
    return svg


def _seed(slug):
    return int(sha1(slug.encode("utf-8")).hexdigest()[:8], 16)


def _shorten(value, limit):
    value = " ".join(value.split())
    return value if len(value) <= limit else value[: limit - 1].rstrip() + "..."


def _infer_motif(category_slug, title, summary, content):
    category_motif = CATEGORY_MOTIFS.get(category_slug)
    if category_motif:
        return category_motif
    return _infer_keyword_motif(f"{title} {summary} {content}") or "everyday"


def _infer_keyword_motif(text):
    lower_text = text.lower()
    for motif, words in KEYWORD_MOTIFS:
        if any(word in lower_text for word in words):
            return motif
    return None


def _background(motif, primary, secondary, warm, accent, seed):
    sun_x = 680 + seed % 90
    hill = 270 + seed % 36
    skyline = ""
    if motif in {"travel", "news", "hero", "movie", "tv", "everyday", "pop"}:
        skyline = f"""
<rect x="540" y="126" width="54" height="164" rx="8" fill="{primary}" opacity=".16"/>
<rect x="606" y="94" width="70" height="196" rx="8" fill="{primary}" opacity=".18"/>
<rect x="692" y="148" width="58" height="142" rx="8" fill="{primary}" opacity=".14"/>
"""
    return f"""
<circle cx="{sun_x}" cy="82" r="58" fill="{warm}" opacity=".45"/>
<circle cx="124" cy="108" r="72" fill="{secondary}" opacity=".15"/>
{skyline}
<path d="M0 {hill} C150 230 260 320 420 282 C590 232 690 316 900 252 L900 420 L0 420 Z" fill="{secondary}" opacity=".18"/>
<path d="M0 334 C180 290 300 376 468 330 C610 292 724 360 900 312 L900 420 L0 420 Z" fill="{accent}" opacity=".16"/>
"""


def _motif(motif, primary, secondary, warm, paper, accent, seed):
    drawers = {
        "travel": _draw_travel,
        "food": _draw_food,
        "music": _draw_music,
        "nature": _draw_nature,
        "tech": _draw_tech,
        "science": _draw_science,
        "sport": _draw_sport,
        "hero": _draw_hero,
        "movie": _draw_movie,
        "game": _draw_game,
        "mystery": _draw_mystery,
        "school": _draw_school,
        "news": _draw_news,
        "wellness": _draw_wellness,
        "anime": _draw_anime,
        "pop": _draw_pop,
        "tv": _draw_tv,
        "history": _draw_history,
        "portrait": _draw_portrait,
        "story": _draw_story,
        "everyday": _draw_everyday,
        "weather": _draw_weather,
    }
    return drawers.get(motif, _draw_everyday)(primary, secondary, warm, paper, accent, seed)


def _object_badge(motif, primary, secondary, warm, accent, seed):
    x = 92 + seed % 34
    y = 286 + seed % 18
    if motif == "food":
        icon = f'<path d="M{x+34} {y+34} h94 a34 34 0 0 1 -34 34 h-26 a34 34 0 0 1 -34 -34 Z" fill="{warm}"/><rect x="{x+58}" y="{y+10}" width="46" height="28" rx="12" fill="#ffffff" opacity=".86"/>'
    elif motif == "travel":
        icon = f'<rect x="{x+22}" y="{y+12}" width="90" height="70" rx="12" fill="{warm}"/><path d="M{x+44} {y+12} v-16 h46 v16" fill="none" stroke="{primary}" stroke-width="8" stroke-linecap="round"/><circle cx="{x+42}" cy="{y+88}" r="8" fill="{primary}"/><circle cx="{x+94}" cy="{y+88}" r="8" fill="{primary}"/>'
    elif motif == "music":
        icon = f'<path d="M{x+70} {y+8} v72" stroke="{primary}" stroke-width="12" stroke-linecap="round"/><path d="M{x+70} {y+8} l70 -18 v28 l-70 18" fill="{warm}"/><circle cx="{x+48}" cy="{y+86}" r="24" fill="{primary}"/>'
    elif motif == "tech":
        icon = f'<rect x="{x+18}" y="{y+18}" width="120" height="72" rx="14" fill="{primary}"/><rect x="{x+34}" y="{y+32}" width="88" height="42" rx="8" fill="{secondary}"/><rect x="{x+2}" y="{y+92}" width="154" height="14" rx="7" fill="{accent}"/>'
    elif motif == "nature":
        icon = f'<path d="M{x+72} {y+8} C{x+132} {y+38} {x+124} {y+96} {x+74} {y+102} C{x+20} {y+86} {x+18} {y+34} {x+72} {y+8} Z" fill="{secondary}"/><path d="M{x+74} {y+96} C{x+70} {y+58} {x+92} {y+34} {x+114} {y+24}" fill="none" stroke="{primary}" stroke-width="7" stroke-linecap="round"/>'
    else:
        icon = f'<rect x="{x+20}" y="{y+12}" width="108" height="78" rx="18" fill="{warm}"/><circle cx="{x+56}" cy="{y+52}" r="10" fill="{primary}"/><circle cx="{x+94}" cy="{y+52}" r="10" fill="{primary}"/><path d="M{x+54} {y+72} C{x+72} {y+86} {x+90} {y+86} {x+108} {y+72}" fill="none" stroke="{primary}" stroke-width="7" stroke-linecap="round"/>'

    return f'<g opacity=".96">{icon}</g>'


def _draw_travel(primary, secondary, warm, paper, accent, seed):
    return f"""
<path d="M250 318 C330 230 448 230 548 318" fill="none" stroke="{primary}" stroke-width="20" stroke-linecap="round" opacity=".82"/>
<path d="M400 318 L470 198 L540 318 Z" fill="{secondary}" opacity=".88"/>
<rect x="560" y="214" width="158" height="78" rx="18" fill="{warm}"/>
<circle cx="596" cy="302" r="14" fill="{primary}"/><circle cx="682" cy="302" r="14" fill="{primary}"/>
<path d="M604 214 v-26 h70 v26" fill="none" stroke="{primary}" stroke-width="9" stroke-linecap="round"/>
"""


def _draw_food(primary, secondary, warm, paper, accent, seed):
    return f"""
<rect x="366" y="260" width="250" height="26" rx="13" fill="{primary}" opacity=".72"/>
<rect x="400" y="180" width="170" height="82" rx="18" fill="{warm}"/>
<path d="M400 206 C434 182 466 230 496 204 C530 176 548 210 570 196 L570 180 L400 180 Z" fill="{accent}" opacity=".9"/>
<rect x="608" y="184" width="76" height="68" rx="18" fill="#ffffff" opacity=".88"/>
<path d="M684 200 C734 200 734 238 684 238" fill="none" stroke="{secondary}" stroke-width="13"/>
<path d="M436 164 v-34 M486 164 v-44 M536 164 v-34" stroke="{primary}" stroke-width="8" stroke-linecap="round"/>
"""


def _draw_music(primary, secondary, warm, paper, accent, seed):
    return f"""
<circle cx="448" cy="218" r="74" fill="{secondary}" opacity=".22"/>
<path d="M460 112 v162" stroke="{primary}" stroke-width="18" stroke-linecap="round"/>
<path d="M460 112 l156 -36 v54 l-156 38" fill="{warm}"/>
<circle cx="404" cy="292" r="44" fill="{primary}"/>
<circle cx="608" cy="252" r="34" fill="{accent}"/>
<path d="M300 156 C340 124 370 124 410 156" fill="none" stroke="{accent}" stroke-width="12" stroke-linecap="round" opacity=".76"/>
"""


def _draw_nature(primary, secondary, warm, paper, accent, seed):
    return f"""
<path d="M296 306 C334 232 386 210 430 306 Z" fill="{secondary}"/>
<path d="M424 306 C482 208 554 202 622 306 Z" fill="{accent}" opacity=".82"/>
<rect x="330" y="230" width="18" height="82" rx="9" fill="{primary}"/>
<circle cx="338" cy="206" r="52" fill="{secondary}"/>
<path d="M534 336 C580 300 636 300 700 338" fill="none" stroke="{primary}" stroke-width="16" stroke-linecap="round" opacity=".46"/>
<path d="M260 340 C350 304 420 376 520 336 C606 304 666 344 738 318" fill="none" stroke="{secondary}" stroke-width="12" stroke-linecap="round"/>
"""


def _draw_tech(primary, secondary, warm, paper, accent, seed):
    return f"""
<rect x="332" y="150" width="262" height="158" rx="22" fill="{primary}"/>
<rect x="360" y="178" width="206" height="96" rx="14" fill="{secondary}"/>
<circle cx="410" cy="226" r="12" fill="{paper}"/>
<circle cx="516" cy="226" r="12" fill="{paper}"/>
<path d="M426 254 C454 272 486 272 514 254" fill="none" stroke="{paper}" stroke-width="8" stroke-linecap="round"/>
<rect x="302" y="314" width="324" height="22" rx="11" fill="{accent}"/>
<path d="M594 184 h74 v100 h-74" fill="none" stroke="{warm}" stroke-width="12" stroke-linejoin="round"/>
"""


def _draw_science(primary, secondary, warm, paper, accent, seed):
    return f"""
<path d="M414 132 h94 v28 l-24 48 v92 a52 52 0 0 1 -104 0 v-92 l-24 -48 v-28 h58" fill="{paper}" stroke="{primary}" stroke-width="10"/>
<path d="M384 274 C420 246 454 304 486 274 C506 260 522 266 536 282 v20 a52 52 0 0 1 -104 0 v-16 C418 272 402 266 384 274 Z" fill="{secondary}" opacity=".86"/>
<circle cx="600" cy="206" r="42" fill="none" stroke="{warm}" stroke-width="9"/>
<path d="M558 206 h84 M600 164 v84" stroke="{warm}" stroke-width="9" stroke-linecap="round"/>
<circle cx="600" cy="206" r="10" fill="{warm}"/>
"""


def _draw_sport(primary, secondary, warm, paper, accent, seed):
    return f"""
<rect x="290" y="202" width="380" height="128" rx="18" fill="{secondary}" opacity=".75"/>
<path d="M290 266 h380 M480 202 v128" stroke="{paper}" stroke-width="8" opacity=".82"/>
<circle cx="482" cy="220" r="62" fill="{warm}"/>
<path d="M430 220 h104 M482 168 v104 M444 184 C470 204 494 204 520 184 M444 256 C470 236 494 236 520 256" stroke="{primary}" stroke-width="7" fill="none"/>
"""


def _draw_hero(primary, secondary, warm, paper, accent, seed):
    return f"""
<path d="M430 132 C470 98 526 104 560 144 L608 304 C540 282 494 284 420 306 Z" fill="{secondary}" opacity=".9"/>
<circle cx="470" cy="166" r="54" fill="{warm}"/>
<path d="M470 120 L486 150 L520 156 L496 180 L502 216 L470 198 L438 216 L444 180 L420 156 L454 150 Z" fill="{primary}"/>
<rect x="580" y="176" width="42" height="118" rx="8" fill="{primary}" opacity=".45"/>
<rect x="640" y="128" width="58" height="166" rx="8" fill="{primary}" opacity=".36"/>
"""


def _draw_movie(primary, secondary, warm, paper, accent, seed):
    return f"""
<rect x="330" y="162" width="290" height="164" rx="20" fill="{primary}"/>
<rect x="360" y="196" width="230" height="90" rx="12" fill="{paper}"/>
<path d="M330 162 l70 -66 h68 l-70 66 M454 162 l70 -66 h68 l-70 66" stroke="{warm}" stroke-width="16"/>
<circle cx="654" cy="202" r="44" fill="{secondary}"/>
<path d="M642 180 l42 22 -42 22 Z" fill="{paper}"/>
"""


def _draw_game(primary, secondary, warm, paper, accent, seed):
    return f"""
<path d="M336 214 C354 174 410 178 450 202 H512 C552 178 608 174 626 214 L662 294 C674 324 644 350 618 332 L564 294 H398 L344 332 C318 350 288 324 300 294 Z" fill="{primary}"/>
<circle cx="396" cy="252" r="14" fill="{paper}"/><circle cx="584" cy="236" r="12" fill="{warm}"/><circle cx="618" cy="266" r="12" fill="{secondary}"/>
<path d="M382 226 v52 M356 252 h52" stroke="{paper}" stroke-width="10" stroke-linecap="round"/>
<rect x="448" y="230" width="70" height="36" rx="12" fill="{accent}"/>
"""


def _draw_mystery(primary, secondary, warm, paper, accent, seed):
    return f"""
<circle cx="448" cy="204" r="76" fill="none" stroke="{primary}" stroke-width="20"/>
<path d="M500 256 L604 340" stroke="{primary}" stroke-width="24" stroke-linecap="round"/>
<path d="M394 202 h106" stroke="{secondary}" stroke-width="10" stroke-linecap="round"/>
<path d="M566 142 h88 v70 h-88 Z" fill="{warm}" opacity=".86"/>
<circle cx="610" cy="176" r="10" fill="{primary}"/>
"""


def _draw_school(primary, secondary, warm, paper, accent, seed):
    return f"""
<rect x="344" y="146" width="104" height="178" rx="14" fill="{primary}"/>
<rect x="462" y="126" width="110" height="198" rx="14" fill="{secondary}"/>
<rect x="586" y="166" width="84" height="158" rx="14" fill="{warm}"/>
<path d="M372 194 h48 M372 226 h48 M490 182 h56 M490 214 h56 M614 218 h30" stroke="{paper}" stroke-width="8" stroke-linecap="round" opacity=".82"/>
<path d="M284 330 h440" stroke="{primary}" stroke-width="16" stroke-linecap="round" opacity=".28"/>
"""


def _draw_news(primary, secondary, warm, paper, accent, seed):
    return f"""
<rect x="326" y="148" width="242" height="176" rx="18" fill="#ffffff" stroke="{primary}" stroke-width="10"/>
<rect x="356" y="182" width="92" height="64" rx="8" fill="{secondary}" opacity=".8"/>
<path d="M470 184 h64 M470 214 h64 M356 268 h176 M356 294 h132" stroke="{primary}" stroke-width="9" stroke-linecap="round" opacity=".72"/>
<circle cx="640" cy="230" r="38" fill="{warm}"/>
<path d="M640 268 v66" stroke="{primary}" stroke-width="12" stroke-linecap="round"/>
"""


def _draw_wellness(primary, secondary, warm, paper, accent, seed):
    return f"""
<rect x="330" y="286" width="304" height="28" rx="14" fill="{secondary}" opacity=".72"/>
<circle cx="480" cy="164" r="42" fill="{warm}"/>
<path d="M480 206 C446 244 426 260 376 268 M480 206 C514 244 536 260 586 268" stroke="{primary}" stroke-width="16" stroke-linecap="round" fill="none"/>
<path d="M450 272 C478 236 510 236 538 272" stroke="{accent}" stroke-width="14" stroke-linecap="round" fill="none"/>
<path d="M636 172 C684 194 686 244 640 264 C606 230 604 194 636 172 Z" fill="{secondary}"/>
"""


def _draw_anime(primary, secondary, warm, paper, accent, seed):
    return f"""
<circle cx="472" cy="184" r="74" fill="{warm}"/>
<path d="M398 172 C426 90 528 82 558 172 C514 150 454 150 398 172 Z" fill="{primary}"/>
<circle cx="444" cy="190" r="16" fill="{primary}"/><circle cx="504" cy="190" r="16" fill="{primary}"/>
<circle cx="450" cy="185" r="6" fill="#ffffff"/><circle cx="510" cy="185" r="6" fill="#ffffff"/>
<path d="M442 226 C464 244 492 244 514 226" fill="none" stroke="{primary}" stroke-width="9" stroke-linecap="round"/>
<path d="M616 116 L630 148 L664 154 L638 176 L646 208 L616 190 L586 208 L594 176 L568 154 L602 148 Z" fill="{accent}"/>
"""


def _draw_pop(primary, secondary, warm, paper, accent, seed):
    return f"""
<rect x="374" y="118" width="164" height="226" rx="28" fill="{primary}"/>
<rect x="398" y="150" width="116" height="154" rx="16" fill="{paper}"/>
<circle cx="456" cy="322" r="10" fill="{paper}"/>
<path d="M566 170 h92 a22 22 0 0 1 22 22 v42 a22 22 0 0 1 -22 22 h-32 l-36 34 v-34 h-24 a22 22 0 0 1 -22 -22 v-42 a22 22 0 0 1 22 -22 Z" fill="{accent}"/>
<path d="M430 214 L446 236 L486 190" stroke="{secondary}" stroke-width="14" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
"""


def _draw_tv(primary, secondary, warm, paper, accent, seed):
    return f"""
<rect x="330" y="150" width="310" height="184" rx="24" fill="{primary}"/>
<rect x="360" y="180" width="250" height="116" rx="14" fill="{paper}"/>
<path d="M434 180 l54 58 -54 58 M516 180 l54 58 -54 58" fill="none" stroke="{secondary}" stroke-width="15" stroke-linecap="round" stroke-linejoin="round" opacity=".8"/>
<path d="M438 334 l-36 42 M532 334 l36 42" stroke="{primary}" stroke-width="12" stroke-linecap="round"/>
<circle cx="632" cy="188" r="16" fill="{warm}"/>
"""


def _draw_history(primary, secondary, warm, paper, accent, seed):
    return f"""
<path d="M336 162 h282 l-34 -48 H370 Z" fill="{primary}"/>
<rect x="366" y="162" width="38" height="148" rx="8" fill="{warm}"/>
<rect x="446" y="162" width="38" height="148" rx="8" fill="{warm}"/>
<rect x="526" y="162" width="38" height="148" rx="8" fill="{warm}"/>
<rect x="324" y="310" width="320" height="28" rx="8" fill="{primary}"/>
<path d="M664 158 c48 18 48 86 0 104 c-26 -28 -26 -76 0 -104 Z" fill="{secondary}" opacity=".75"/>
"""


def _draw_portrait(primary, secondary, warm, paper, accent, seed):
    return f"""
<rect x="358" y="114" width="236" height="230" rx="22" fill="#ffffff" stroke="{primary}" stroke-width="12"/>
<circle cx="476" cy="190" r="52" fill="{warm}"/>
<path d="M408 304 C424 252 528 252 544 304 Z" fill="{secondary}"/>
<path d="M432 176 C452 126 516 126 536 176 C494 160 470 160 432 176 Z" fill="{primary}"/>
<path d="M424 336 h104" stroke="{accent}" stroke-width="10" stroke-linecap="round"/>
"""


def _draw_story(primary, secondary, warm, paper, accent, seed):
    return f"""
<path d="M330 166 C388 132 442 142 482 184 C522 142 576 132 634 166 v150 C574 286 524 296 482 338 C440 296 390 286 330 316 Z" fill="#ffffff" stroke="{primary}" stroke-width="12"/>
<path d="M482 184 v154" stroke="{primary}" stroke-width="8" opacity=".4"/>
<path d="M374 210 h70 M374 240 h78 M520 210 h70 M520 240 h78" stroke="{secondary}" stroke-width="8" stroke-linecap="round"/>
<path d="M626 128 L674 176 L626 224 L578 176 Z" fill="{warm}" opacity=".84"/>
"""


def _draw_everyday(primary, secondary, warm, paper, accent, seed):
    return f"""
<rect x="350" y="178" width="230" height="154" rx="18" fill="{secondary}" opacity=".86"/>
<path d="M330 190 L466 100 L604 190 Z" fill="{primary}"/>
<rect x="432" y="244" width="66" height="88" rx="10" fill="{warm}"/>
<rect x="390" y="218" width="46" height="42" rx="8" fill="{paper}" opacity=".9"/>
<rect x="516" y="218" width="46" height="42" rx="8" fill="{paper}" opacity=".9"/>
<path d="M632 270 h78 v44 h-78 z" fill="{accent}" opacity=".8"/>
<circle cx="648" cy="322" r="10" fill="{primary}"/><circle cx="694" cy="322" r="10" fill="{primary}"/>
"""


def _draw_weather(primary, secondary, warm, paper, accent, seed):
    return f"""
<ellipse cx="456" cy="188" rx="96" ry="46" fill="{paper}" stroke="{primary}" stroke-width="10"/>
<ellipse cx="386" cy="198" rx="52" ry="32" fill="{paper}" stroke="{primary}" stroke-width="10"/>
<ellipse cx="534" cy="202" rx="58" ry="34" fill="{paper}" stroke="{primary}" stroke-width="10"/>
<path d="M394 274 l-26 48 M462 274 l-26 48 M530 274 l-26 48" stroke="{secondary}" stroke-width="11" stroke-linecap="round"/>
<circle cx="640" cy="140" r="46" fill="{warm}"/>
"""
