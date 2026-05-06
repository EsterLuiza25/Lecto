CANVAS = 'viewBox="0 0 512 720" width="512" height="720"'


def build_cartoon_avatar_svg(option):
    palette = {
        "ink": "#27212A",
        "line": "#3A2927",
        "skin_light": "#F2B981",
        "skin_medium": "#C77C55",
        "skin_dark": "#774534",
        "skin_warm": "#B96D4A",
        "skin_gold": "#D8A25F",
        "shirt_blue": "#16A7D9",
        "shirt_pink": "#F55F7D",
        "shirt_teal": "#27A19A",
        "shirt_navy": "#263A66",
        "shirt_gold": "#E7B84A",
        "short_orange": "#F4A63E",
        "short_denim": "#2877A8",
        "hair_brown": "#3A1D13",
        "hair_black": "#241D25",
        "hair_orange": "#A94C2E",
        "hair_teal": "#1C566D",
        "violet": "#8F55AD",
        "white": "#FFFDF7",
        "shoe": "#304563",
        "gold": "#E5B747",
    }
    name = option.name.lower()
    layer = option.option_type

    renderers = {
        "base_body": _base_body,
        "body_style": _body_style,
        "hair_style": _hair_style,
        "eyes": _eyes,
        "outfit": _outfit,
        "accessory": _accessory,
    }
    shapes = renderers.get(layer, lambda *_: "")(name, palette)

    return f"""<svg xmlns="http://www.w3.org/2000/svg" {CANVAS} role="img" aria-label="{option.name}">
<title>{option.name}</title>
{_defs(palette, _skin(name, palette))}
<g filter="url(#shadow)">
{shapes}
</g>
</svg>
"""


def _skin(name, palette):
    if "media" in name:
        return palette["skin_medium"]
    if "escura" in name:
        return palette["skin_dark"]
    if "quente" in name:
        return palette["skin_warm"]
    if "dourada" in name:
        return palette["skin_gold"]
    return palette["skin_light"]


def _shade(skin, palette):
    if skin == palette["skin_dark"]:
        return "#4B2B23"
    if skin == palette["skin_medium"]:
        return "#8D4F37"
    return "#A56543"


def _base_body(name, p):
    skin = _skin(name, p)
    shade = _shade(skin, p)
    return f"""
<ellipse cx="256" cy="670" rx="128" ry="18" fill="#173245" opacity=".16"/>

<path d="M210 441 C202 502 198 560 191 620" fill="none" stroke="{skin}" stroke-width="30" stroke-linecap="round"/>
<path d="M302 441 C310 502 314 560 321 620" fill="none" stroke="{skin}" stroke-width="30" stroke-linecap="round"/>
<path d="M182 620 C207 608 241 611 250 634 C221 646 181 646 158 635 C158 628 166 623 182 620 Z" fill="{p['white']}" stroke="{p['line']}" stroke-width="6" stroke-linejoin="round"/>
<path d="M330 620 C305 608 271 611 262 634 C291 646 331 646 354 635 C354 628 346 623 330 620 Z" fill="{p['white']}" stroke="{p['line']}" stroke-width="6" stroke-linejoin="round"/>
<path d="M174 637 H250" stroke="{p['shoe']}" stroke-width="11" stroke-linecap="round"/>
<path d="M262 637 H338" stroke="{p['shoe']}" stroke-width="11" stroke-linecap="round"/>

<path d="M204 348 C165 381 144 426 134 492" fill="none" stroke="{skin}" stroke-width="28" stroke-linecap="round"/>
<path d="M308 348 C347 381 368 426 378 492" fill="none" stroke="{skin}" stroke-width="28" stroke-linecap="round"/>
<circle cx="133" cy="496" r="18" fill="{skin}" stroke="{p['line']}" stroke-width="6"/>
<circle cx="379" cy="496" r="18" fill="{skin}" stroke="{p['line']}" stroke-width="6"/>

<path d="M228 266 H284 L294 335 C274 351 238 351 218 335 Z" fill="{skin}" stroke="{p['line']}" stroke-width="6" stroke-linejoin="round"/>
<ellipse cx="173" cy="179" rx="20" ry="27" fill="{skin}" stroke="{p['line']}" stroke-width="6"/>
<ellipse cx="339" cy="179" rx="20" ry="27" fill="{skin}" stroke="{p['line']}" stroke-width="6"/>
<path d="M176 179 C185 177 188 188 180 196" fill="none" stroke="{shade}" stroke-width="4" stroke-linecap="round" opacity=".55"/>
<path d="M336 179 C327 177 324 188 332 196" fill="none" stroke="{shade}" stroke-width="4" stroke-linecap="round" opacity=".55"/>
<ellipse cx="256" cy="175" rx="84" ry="96" fill="url(#skin)" stroke="{p['line']}" stroke-width="7"/>
<ellipse cx="222" cy="214" rx="18" ry="9" fill="#EB6F74" opacity=".18"/>
<ellipse cx="290" cy="214" rx="18" ry="9" fill="#EB6F74" opacity=".18"/>
<path d="M256 181 C248 204 250 218 262 224" fill="none" stroke="{shade}" stroke-width="5" stroke-linecap="round" opacity=".34"/>
"""


def _body_style(name, p):
    if "feminino" in name:
        return f"""
<path d="M200 327 C223 305 289 305 312 327" fill="none" stroke="{p['shirt_pink']}" stroke-width="8" stroke-linecap="round" opacity=".48"/>
<path d="M212 403 C235 423 277 423 300 403" fill="none" stroke="{p['shirt_pink']}" stroke-width="7" stroke-linecap="round" opacity=".34"/>
"""
    return f"""
<path d="M186 327 C213 305 299 305 326 327" fill="none" stroke="{p['shirt_navy']}" stroke-width="8" stroke-linecap="round" opacity=".5"/>
<path d="M205 404 C232 418 280 418 307 404" fill="none" stroke="{p['shirt_navy']}" stroke-width="7" stroke-linecap="round" opacity=".32"/>
"""


def _hair_style(name, p):
    if "turquesa" in name:
        return f"""
<path d="M171 164 C174 84 255 43 324 87 C358 109 357 169 335 213 C311 182 269 163 226 174 C202 180 184 177 171 164 Z" fill="url(#hairTeal)" stroke="{p['line']}" stroke-width="7" stroke-linejoin="round"/>
<path d="M201 101 C194 139 216 159 248 172 C225 174 200 187 182 204 C168 160 174 124 201 101 Z" fill="#182936" opacity=".35"/>
"""
    if "laranja" in name:
        return f"""
<path d="M170 164 C179 82 294 58 338 124 C361 160 345 227 316 270 C311 220 291 182 249 171 C218 164 192 178 170 207 Z" fill="url(#hairOrange)" stroke="{p['line']}" stroke-width="7" stroke-linejoin="round"/>
<path d="M204 111 C231 79 292 84 325 130 C284 119 235 130 204 164 Z" fill="#FF8C57" opacity=".72"/>
"""
    if "cacheado" in name:
        return f"""
<circle cx="181" cy="160" r="32" fill="{p['hair_brown']}" stroke="{p['line']}" stroke-width="6"/>
<circle cx="209" cy="108" r="35" fill="{p['hair_brown']}" stroke="{p['line']}" stroke-width="6"/>
<circle cx="256" cy="88" r="40" fill="{p['hair_brown']}" stroke="{p['line']}" stroke-width="6"/>
<circle cx="308" cy="113" r="36" fill="{p['hair_brown']}" stroke="{p['line']}" stroke-width="6"/>
<circle cx="333" cy="162" r="32" fill="{p['hair_brown']}" stroke="{p['line']}" stroke-width="6"/>
<path d="M183 187 C222 154 297 154 331 187 C289 174 222 174 183 187 Z" fill="#27120D"/>
"""
    if "preto longo" in name:
        return f"""
<path d="M165 146 C169 73 343 73 347 146 L336 330 C298 360 214 360 176 330 Z" fill="{p['hair_black']}" stroke="{p['line']}" stroke-width="7" stroke-linejoin="round"/>
<path d="M183 156 C214 105 298 105 329 156 C287 139 225 139 183 156 Z" fill="#3C3039"/>
"""
    if "castanho" in name:
        return f"""
<path d="M168 161 C176 84 326 70 346 148 C318 124 264 121 230 136 C207 145 188 156 168 161 Z" fill="#704025" stroke="{p['line']}" stroke-width="7" stroke-linejoin="round"/>
<path d="M178 184 C211 135 284 113 337 160 C291 150 230 163 178 184 Z" fill="#92522F"/>
"""
    if "careca" in name:
        return f"""
<path d="M193 157 C218 123 294 123 319 157" fill="none" stroke="{p['line']}" stroke-width="7" stroke-linecap="round" opacity=".3"/>
<path d="M197 137 C226 115 286 115 315 137" fill="none" stroke="#FFFFFF" stroke-width="8" stroke-linecap="round" opacity=".16"/>
"""
    if "lenco" in name:
        return f"""
<path d="M170 160 C172 80 340 80 342 160 L330 314 C294 343 218 343 182 314 Z" fill="{p['hair_black']}" stroke="{p['line']}" stroke-width="7" stroke-linejoin="round"/>
<path d="M179 151 C211 98 301 98 333 151 C291 135 221 135 179 151 Z" fill="{p['violet']}" stroke="{p['line']}" stroke-width="6"/>
<path d="M222 126 C244 141 269 141 292 126" fill="none" stroke="{p['shirt_pink']}" stroke-width="7" stroke-linecap="round"/>
<circle cx="310" cy="86" r="22" fill="{p['hair_black']}" stroke="{p['line']}" stroke-width="6"/>
"""
    return f"""
<path d="M168 161 C168 94 222 57 284 68 C334 76 356 119 343 172 C314 144 286 132 250 144 C221 154 194 172 170 194 Z" fill="url(#hairBrown)" stroke="{p['line']}" stroke-width="7" stroke-linejoin="round"/>
<path d="M194 116 C212 154 262 148 300 129 C289 163 241 184 188 185 C178 154 180 131 194 116 Z" fill="#21140F"/>
<path d="M213 82 C203 114 217 138 250 150" fill="none" stroke="#FFFFFF" stroke-width="10" stroke-linecap="round" opacity=".14"/>
"""


def _eyes(name, p):
    if "felizes" in name:
        eyes = f'<path d="M217 178 C226 169 238 169 247 178" fill="none" stroke="{p["ink"]}" stroke-width="8" stroke-linecap="round"/><path d="M265 178 C274 169 286 169 295 178" fill="none" stroke="{p["ink"]}" stroke-width="8" stroke-linecap="round"/>'
    elif "serenos" in name:
        eyes = f'<path d="M216 181 H246" stroke="{p["ink"]}" stroke-width="7" stroke-linecap="round"/><path d="M266 181 H296" stroke="{p["ink"]}" stroke-width="7" stroke-linecap="round"/>'
    elif "piscadinha" in name:
        eyes = f'<circle cx="231" cy="179" r="10" fill="{p["ink"]}"/><circle cx="235" cy="175" r="3" fill="#FFFFFF"/><path d="M266 179 H296" stroke="{p["ink"]}" stroke-width="8" stroke-linecap="round"/>'
    elif "focados" in name:
        eyes = f'<path d="M212 162 L246 170" stroke="{p["ink"]}" stroke-width="6" stroke-linecap="round"/><path d="M266 170 L300 162" stroke="{p["ink"]}" stroke-width="6" stroke-linecap="round"/><circle cx="230" cy="181" r="10" fill="{p["ink"]}"/><circle cx="282" cy="181" r="10" fill="{p["ink"]}"/>'
    else:
        eyes = f'<circle cx="230" cy="179" r="11" fill="{p["ink"]}"/><circle cx="282" cy="179" r="11" fill="{p["ink"]}"/><circle cx="234" cy="175" r="3.5" fill="#FFFFFF"/><circle cx="286" cy="175" r="3.5" fill="#FFFFFF"/>'
    return f"""
{eyes}
<path d="M226 233 C243 250 269 250 286 233" fill="none" stroke="{p['ink']}" stroke-width="8" stroke-linecap="round"/>
"""


def _outfit(name, p):
    shirt, shorts, accent = p["shirt_blue"], p["short_orange"], "#043B56"
    if "coral" in name:
        shirt, shorts, accent = p["shirt_pink"], p["short_denim"], "#FFFFFF"
    elif "violeta" in name:
        shirt, shorts, accent = p["violet"], p["shirt_navy"], p["gold"]
    elif "turquesa" in name:
        shirt, shorts, accent = p["shirt_teal"], p["short_denim"], "#FFFFFF"
    elif "jaqueta" in name:
        shirt, shorts, accent = p["shirt_navy"], p["short_denim"], p["gold"]
    elif "sueter" in name:
        shirt, shorts, accent = p["shirt_gold"], p["shirt_navy"], p["shirt_navy"]
    elif "cachecol" in name:
        shirt, shorts, accent = p["shirt_navy"], p["short_denim"], p["gold"]

    extra = ""
    if "jaqueta" in name:
        extra = f'<path d="M256 317 V452" stroke="{accent}" stroke-width="7" stroke-linecap="round"/><circle cx="242" cy="374" r="5" fill="{accent}"/><circle cx="270" cy="374" r="5" fill="{accent}"/>'
    elif "sueter" in name:
        extra = f'<path d="M191 380 H321" stroke="{accent}" stroke-width="10" stroke-linecap="round" opacity=".78"/>'
    elif "cachecol" in name:
        extra = f'<path d="M202 318 C233 336 280 336 311 318 L321 348 C286 368 226 368 191 348 Z" fill="{accent}" stroke="{p["line"]}" stroke-width="5"/><rect x="288" y="340" width="28" height="84" rx="12" fill="{accent}" stroke="{p["line"]}" stroke-width="5"/>'

    return f"""
<path d="M190 320 C209 300 303 300 322 320 L346 409 C318 429 194 429 166 409 Z" fill="{shirt}" stroke="{p['line']}" stroke-width="7" stroke-linejoin="round"/>
<path d="M190 320 L147 372 L172 394 L210 347" fill="{shirt}" stroke="{p['line']}" stroke-width="7" stroke-linejoin="round"/>
<path d="M322 320 L365 372 L340 394 L302 347" fill="{shirt}" stroke="{p['line']}" stroke-width="7" stroke-linejoin="round"/>
<path d="M230 317 L256 345 L282 317" fill="none" stroke="{accent}" stroke-width="7" stroke-linecap="round" stroke-linejoin="round" opacity=".92"/>
<path d="M199 424 H313 L328 504 C305 517 279 511 256 498 C233 511 207 517 184 504 Z" fill="{shorts}" stroke="{p['line']}" stroke-width="7" stroke-linejoin="round"/>
<path d="M256 438 V501" stroke="{p['line']}" stroke-width="5" stroke-linecap="round" opacity=".35"/>
<path d="M210 596 H240" stroke="#FFFFFF" stroke-width="7" stroke-linecap="round"/>
<path d="M272 596 H302" stroke="#FFFFFF" stroke-width="7" stroke-linecap="round"/>
{extra}
"""


def _accessory(name, p):
    if "oculos" in name:
        return f"""
<circle cx="228" cy="181" r="29" fill="#FFFFFF" opacity=".12" stroke="{p['ink']}" stroke-width="7"/>
<circle cx="284" cy="181" r="29" fill="#FFFFFF" opacity=".12" stroke="{p['ink']}" stroke-width="7"/>
<path d="M257 181 H255" stroke="{p['ink']}" stroke-width="7" stroke-linecap="round"/>
<path d="M199 174 L182 164 M313 174 L330 164" stroke="{p['ink']}" stroke-width="6" stroke-linecap="round"/>
"""
    if "fones" in name:
        return f"""
<path d="M178 184 C179 88 333 88 334 184" fill="none" stroke="{p['shirt_navy']}" stroke-width="12" stroke-linecap="round"/>
<rect x="152" y="166" width="36" height="64" rx="16" fill="{p['shirt_teal']}" stroke="{p['line']}" stroke-width="6"/>
<rect x="324" y="166" width="36" height="64" rx="16" fill="{p['shirt_teal']}" stroke="{p['line']}" stroke-width="6"/>
"""
    if "brinco" in name:
        return f"""
<circle cx="174" cy="215" r="7" fill="{p['gold']}" stroke="{p['line']}" stroke-width="3"/>
<circle cx="338" cy="215" r="7" fill="{p['gold']}" stroke="{p['line']}" stroke-width="3"/>
<circle cx="174" cy="234" r="6" fill="{p['gold']}" opacity=".9"/>
<circle cx="338" cy="234" r="6" fill="{p['gold']}" opacity=".9"/>
"""
    if "gravata" in name:
        return f"""
<path d="M224 333 L256 314 L288 333 L256 353 Z" fill="{p['shirt_pink']}" stroke="{p['line']}" stroke-width="5" stroke-linejoin="round"/>
<path d="M256 353 L276 426 H236 Z" fill="{p['shirt_pink']}" stroke="{p['line']}" stroke-width="5" stroke-linejoin="round"/>
"""
    if "gorro" in name:
        return f"""
<path d="M181 96 H331 L256 47 Z" fill="{p['shirt_navy']}" stroke="{p['line']}" stroke-width="7" stroke-linejoin="round"/>
<rect x="190" y="93" width="132" height="19" rx="9" fill="{p['gold']}" stroke="{p['line']}" stroke-width="5"/>
<path d="M328 100 C364 116 365 157 328 177" fill="none" stroke="{p['gold']}" stroke-width="8" stroke-linecap="round"/>
<circle cx="329" cy="180" r="8" fill="{p['gold']}"/>
"""
    return f"""
<rect x="342" y="370" width="61" height="90" rx="11" fill="{p['gold']}" stroke="{p['line']}" stroke-width="7"/>
<path d="M357 400 H388 M357 421 H381" stroke="{p['line']}" stroke-width="6" stroke-linecap="round"/>
<path d="M339 378 C319 396 314 428 330 454" fill="none" stroke="{p['line']}" stroke-width="6" stroke-linecap="round"/>
"""


def _defs(p, skin):
    shade = _shade(skin, p)
    return f"""
<defs>
  <radialGradient id="skin" cx="35%" cy="20%" r="82%">
    <stop offset="0" stop-color="#FFFFFF" stop-opacity=".58"/>
    <stop offset=".36" stop-color="{skin}"/>
    <stop offset="1" stop-color="{shade}" stop-opacity=".55"/>
  </radialGradient>
  <linearGradient id="hairBrown" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="#7D3B1F"/>
    <stop offset=".46" stop-color="{p['hair_brown']}"/>
    <stop offset="1" stop-color="#160B08"/>
  </linearGradient>
  <linearGradient id="hairTeal" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="#4BC4C0"/>
    <stop offset=".52" stop-color="{p['hair_teal']}"/>
    <stop offset="1" stop-color="#14222E"/>
  </linearGradient>
  <linearGradient id="hairOrange" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="#FF9860"/>
    <stop offset=".55" stop-color="{p['hair_orange']}"/>
    <stop offset="1" stop-color="#4B2117"/>
  </linearGradient>
  <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">
    <feDropShadow dx="0" dy="10" stdDeviation="8" flood-color="#1C4259" flood-opacity=".18"/>
  </filter>
</defs>
"""
