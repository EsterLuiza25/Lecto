import json
import os
import re
from dataclasses import dataclass


DEFAULT_MODEL = os.getenv("LECTO_AI_MODEL", "gpt-4o-mini")

COMMON_TRANSLATIONS = {
    "a": "um/uma",
    "an": "um/uma",
    "and": "e",
    "are": "sao/estao",
    "because": "porque",
    "big": "grande",
    "but": "mas",
    "can": "pode/consegue",
    "city": "cidade",
    "day": "dia",
    "does": "faz",
    "fast": "rapido",
    "for": "para/por",
    "from": "de",
    "has": "tem",
    "have": "tem/ter",
    "helps": "ajuda",
    "in": "em/dentro de",
    "is": "e/esta",
    "it": "ele/ela/isso",
    "many": "muitos",
    "new": "novo",
    "not": "nao",
    "of": "de",
    "on": "em/sobre",
    "people": "pessoas",
    "reads": "le",
    "robot": "robo",
    "short": "curto",
    "small": "pequeno",
    "smiles": "sorri",
    "table": "mesa",
    "tea": "cha",
    "text": "texto",
    "the": "o/a/os/as",
    "there": "ha/existe",
    "they": "eles/elas",
    "this": "este/esta/isto",
    "to": "para",
    "very": "muito",
    "with": "com",
}


@dataclass(frozen=True)
class ReadabilityMetrics:
    word_count: int
    sentence_count: int
    average_sentence_length: float
    long_word_ratio: float
    suggested_level: str


def generate_quiz_from_text(text_content):
    """
    Return 5 multiple-choice questions for a text.

    When OPENAI_API_KEY is configured and the openai package is installed, this
    calls an LLM. Otherwise it returns a deterministic local fallback so tests,
    local development, and deploy health checks do not depend on external APIs.
    """
    prompt = (
        "Create exactly 5 English reading-comprehension questions for this text. "
        "Return only JSON as a list. Each item must have: question, options. "
        "options must have exactly 4 items with text and is_correct. Text:\n\n"
        f"{text_content}"
    )
    payload = _call_llm_json(prompt)
    if payload:
        normalized = _normalize_quiz_payload(payload)
        if normalized:
            return normalized[:5]

    return _fallback_quiz(text_content)


def analyze_text_difficulty(text_content):
    metrics = _readability_metrics(text_content)
    return {
        "word_count": metrics.word_count,
        "sentence_count": metrics.sentence_count,
        "average_sentence_length": metrics.average_sentence_length,
        "long_word_ratio": metrics.long_word_ratio,
        "suggested_level": metrics.suggested_level,
    }


def explain_selection(selection, context="", glossary=None):
    prompt = (
        "Explain this English passage for a Brazilian Portuguese learner. "
        "Return JSON with keys: explanation_pt, key_words, grammar_note_pt. "
        f"Context: {context}\n\nSelection: {selection}"
    )
    payload = _call_llm_json(prompt)
    if isinstance(payload, dict):
        return {
            "selection": selection,
            "explanation_pt": payload.get("explanation_pt") or _fallback_explanation(selection),
            "key_words": payload.get("key_words") or [],
            "grammar_note_pt": payload.get("grammar_note_pt") or "",
            "source": "llm",
        }

    local = _local_explanation(selection, glossary=glossary)
    return {
        "selection": selection,
        "explanation_pt": local["explanation_pt"],
        "key_words": local["key_words"],
        "grammar_note_pt": local["grammar_note_pt"],
        "source": "local_fallback",
    }


def _call_llm_json(prompt):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None

    try:
        from openai import OpenAI
    except ImportError:
        return None

    try:
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "You are an assistant that returns strict JSON for an English-learning app.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
            response_format={"type": "json_object"},
        )
        content = response.choices[0].message.content
        parsed = json.loads(content)
        return parsed.get("questions") if isinstance(parsed, dict) and "questions" in parsed else parsed
    except Exception:
        return None


def _normalize_quiz_payload(payload):
    if isinstance(payload, dict):
        payload = payload.get("questions", [])
    if not isinstance(payload, list):
        return []

    questions = []
    for item in payload:
        question = str(item.get("question", "")).strip() if isinstance(item, dict) else ""
        options = item.get("options", []) if isinstance(item, dict) else []
        if not question or len(options) < 2:
            continue

        normalized_options = []
        has_correct = False
        for option in options[:4]:
            if not isinstance(option, dict):
                continue
            text = str(option.get("text", "")).strip()
            is_correct = bool(option.get("is_correct"))
            if not text:
                continue
            has_correct = has_correct or is_correct
            normalized_options.append({"text": text, "is_correct": is_correct})

        if len(normalized_options) >= 2 and has_correct:
            questions.append({"question": question, "options": normalized_options[:4]})

    return questions


def _fallback_quiz(text_content):
    sentences = _sentences(text_content)
    first_sentence = sentences[0] if sentences else "The text presents a short idea."
    topic = " ".join(_words(first_sentence)[:6]) or "the text"

    questions = []
    stems = [
        "What is the main idea of the passage?",
        "Which sentence best matches the text?",
        "What should the reader understand from the passage?",
        "Which option is supported by the text?",
        "What is a good summary of the passage?",
    ]
    for index, stem in enumerate(stems, start=1):
        questions.append(
            {
                "question": stem,
                "options": [
                    {"text": f"The passage is mainly about {topic}.", "is_correct": True},
                    {"text": "The passage is about an unrelated historical event.", "is_correct": False},
                    {"text": "The passage only lists random words.", "is_correct": False},
                    {"text": "The passage avoids giving any central idea.", "is_correct": False},
                ],
            }
        )
    return questions


def _readability_metrics(text_content):
    words = _words(text_content)
    sentences = _sentences(text_content)
    word_count = len(words)
    sentence_count = max(1, len(sentences))
    average = round(word_count / sentence_count, 2)
    long_words = [word for word in words if len(word) >= 8]
    long_ratio = round(len(long_words) / max(1, word_count), 2)

    if word_count <= 80 and average <= 10:
        level = "Iniciante"
    elif word_count <= 120 and average <= 12:
        level = "A1"
    elif word_count <= 180 and average <= 15:
        level = "A2"
    elif word_count <= 260 and average <= 18:
        level = "B1"
    elif word_count <= 380 and long_ratio <= 0.24:
        level = "B2"
    elif word_count <= 550:
        level = "C1"
    else:
        level = "C2"

    return ReadabilityMetrics(
        word_count=word_count,
        sentence_count=sentence_count,
        average_sentence_length=average,
        long_word_ratio=long_ratio,
        suggested_level=level,
    )


def _local_explanation(selection, glossary=None):
    clean = " ".join(selection.split())
    words = _words(clean)
    glossary_lookup = _normalize_glossary(glossary)
    translations = _translated_terms(words, glossary_lookup)
    approximate = _approximate_translation(words, glossary_lookup)
    grammar_note = _grammar_note(clean)
    focus = _main_focus(words, translations)

    parts = [f"Trecho selecionado: \"{clean[:220]}\"."]
    if approximate:
        parts.append(f"Traducao aproximada: {approximate}.")
    if focus:
        parts.append(f"Ideia principal: o trecho fala sobre {focus}.")
    if translations:
        terms = "; ".join(f"{item['word']} = {item['translation']}" for item in translations[:8])
        parts.append(f"Palavras-chave: {terms}.")

    return {
        "explanation_pt": " ".join(parts),
        "key_words": translations[:8],
        "grammar_note_pt": grammar_note,
    }


def _normalize_glossary(glossary):
    if not glossary:
        return {}

    normalized = {}
    for key, value in glossary.items():
        if not key or not value:
            continue
        normalized[str(key).strip().lower()] = str(value).strip()
    return normalized


def _translated_terms(words, glossary_lookup):
    seen = set()
    terms = []
    for word in words:
        normalized = word.lower()
        translation = glossary_lookup.get(normalized) or COMMON_TRANSLATIONS.get(normalized)
        if not translation or normalized in seen:
            continue
        seen.add(normalized)
        terms.append({"word": word, "translation": translation})
    return terms


def _approximate_translation(words, glossary_lookup):
    translated = []
    for word in words[:28]:
        normalized = word.lower()
        translated.append(glossary_lookup.get(normalized) or COMMON_TRANSLATIONS.get(normalized) or f"[{word}]")
    return " ".join(translated).strip()


def _grammar_note(selection):
    lowered = selection.lower()
    if re.search(r"\bthere is\b", lowered):
        return "'There is' indica existencia no singular: em portugues, normalmente vira 'ha' ou 'existe'."
    if re.search(r"\bthere are\b", lowered):
        return "'There are' indica existencia no plural: em portugues, normalmente vira 'ha' ou 'existem'."
    if re.search(r"\b(can|could)\b", lowered):
        return "'Can' e 'could' indicam capacidade, possibilidade ou permissao, dependendo do contexto."
    if re.search(r"\b(must|should|have to)\b", lowered):
        return "O trecho usa verbo modal para indicar obrigacao, conselho ou necessidade."
    if re.search(r"\b(was|were|had|did)\b", lowered) or re.search(r"\b\w+ed\b", lowered):
        return "O trecho parece usar passado; observe o verbo para entender a acao concluida."
    if re.search(r"\b(is|are|am)\b", lowered):
        return "O trecho usa presente com o verbo 'to be', geralmente para descrever estado, identidade ou localizacao."
    return "Leia primeiro o sujeito, depois o verbo principal, e por fim os complementos que explicam lugar, tempo ou motivo."


def _main_focus(words, translations):
    meaningful = [
        item["translation"]
        for item in translations
        if item["word"].lower() not in {"a", "an", "the", "is", "are", "there", "on", "in", "of", "to"}
    ]
    if meaningful:
        return ", ".join(meaningful[:4])

    long_words = [word for word in words if len(word) > 4]
    if long_words:
        return ", ".join(long_words[:3])
    return ""


def _fallback_keywords(selection):
    words = [word.lower() for word in _words(selection) if len(word) > 4]
    return sorted(set(words))[:6]


def _words(text):
    return re.findall(r"[A-Za-z][A-Za-z'-]*", text or "")


def _sentences(text):
    return [item.strip() for item in re.split(r"(?<=[.!?])\s+", text or "") if item.strip()]
