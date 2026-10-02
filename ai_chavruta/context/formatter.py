"""Renders a selected_context dict (see selectors.py) into plain text for
the LLM prompt. One renderer per section shape — each section in
INTENT_CONTEXT_MAP has a distinct structure (see parser.py/dafyomi_client.py)."""


def _format_gemara(items):
    lines = []
    for seg in items:
        lines.append(f"[{seg['ref']}]")
        if seg.get("en"):
            lines.append(f"English: {seg['en']}")
        if seg.get("he"):
            lines.append(f"Hebrew: {seg['he']}")
    return "\n".join(lines)


def _format_source_list(items, label):
    lines = []
    for item in items:
        header = item.get("ref") or item.get("commentator") or label
        lines.append(f"[{header}]")
        if item.get("en"):
            lines.append(item["en"])
        elif item.get("he"):
            lines.append(item["he"])
    return "\n".join(lines)


def _format_tosafot(points):
    lines = []
    for point in points:
        lines.append(f"Tosafot DH {point['subject_en']}")
        if point.get("summary"):
            lines.append(f"Summary: {point['summary']}")
        for entry in point.get("entries", []):
            prefix = f"{entry['label']} {entry['type']}:".strip()
            lines.append(f"  {prefix} {entry['en']}".strip())
    return "\n".join(lines)


def _format_insights(points):
    lines = []
    for point in points:
        lines.append(f"Topic: {point['subject']}")
        for entry in point.get("entries", []):
            prefix = entry["label"]
            lines.append(f"  {prefix} {entry['text']}".strip())
    return "\n".join(lines)


def _format_halacha_topics(topics):
    lines = []
    for topic in topics:
        lines.append(f"Halachic topic: {topic['subject']}")
        for entry in topic.get("entries", []):
            prefix = f"{entry['label']} {entry['type']}:".strip()
            lines.append(f"  {prefix} {entry['text']}".strip())
        if topic.get("see_also"):
            lines.append(f"  See also: {', '.join(topic['see_also'])}")
    return "\n".join(lines)


def _format_vocabulary(terms):
    lines = []
    for term in terms:
        lines.append(f"{term['line']} {term['definition']}".strip())
        for point in term.get("points", []):
            lines.append(f"  {point['label']} {point['text']}".strip())
    return "\n".join(lines)


_SECTION_RENDERERS = {
    "gemara": (_format_gemara, "Gemara"),
    "rashi": (lambda items: _format_source_list(items, "Rashi"), "Rashi"),
    "mishnah": (lambda items: _format_source_list(items, "Mishnah"), "Mishnah"),
    "halacha": (lambda items: _format_source_list(items, "Halachic source"), "Halachic Sources"),
    "other_commentaries": (lambda items: _format_source_list(items, "Commentary"), "Other Commentaries"),
    "links": (lambda items: _format_source_list(items, "Reference"), "Related Sources"),
    "tosafot": (_format_tosafot, "Tosafot"),
    "insights": (_format_insights, "Insights"),
    "halacha_topics": (_format_halacha_topics, "Halacha (Gemara -> Rishonim -> Poskim)"),
    "vocabulary": (_format_vocabulary, "Vocabulary"),
}

# Order sections from most universally used to most intent-specific, so a
# narrower per-intent context stays a prefix of a broader one — helps
# provider-side prompt caching across intent switches within a session.
_SECTION_ORDER = [
    "gemara", "rashi", "tosafot", "insights", "mishnah", "halacha",
    "halacha_topics", "other_commentaries", "links", "vocabulary",
]


def format_context_for_prompt(selected_context):
    blocks = []
    for key in _SECTION_ORDER:
        items = selected_context.get(key)
        if not items:
            continue
        renderer, title = _SECTION_RENDERERS[key]
        text = renderer(items)
        if text:
            blocks.append(f"=== {title} ===\n{text}")
    return "\n\n".join(blocks)
