"""
Normalizes raw Sefaria daf data into the categorized structure the LangGraph
nodes/prompts consume.

"gemara" is built from the Steinsaltz elucidation rather than the raw
Aramaic source text — Hebrew from the "Steinsaltz" commentary (a link,
one per Gemara segment), English from the William Davidson Edition (Sefaria's
English translation, based on Steinsaltz's work). Raw Aramaic is much
harder for both the LLM and the end user to work with directly.

"tosafot" is intentionally NOT populated here — it's sourced separately from
dafyomi.co.il's point-by-point Tosafot summaries (see dafyomi_client.py),
which are far more usable as context than Sefaria's terse Tosafot text.
Sefaria's own Tosafot links fall through into "other_commentaries" below so
that data isn't simply discarded.

Sefaria's `category` field alone isn't specific enough to identify Rashi —
"Commentary" mixes Rashi with dozens of other commentators. `collectiveTitle`
identifies the actual commentator/work.
"""
from django.utils.html import strip_tags

RASHI_TITLE = "Rashi"
STEINSALTZ_TITLE = "Steinsaltz"
DAVIDSON_ENGLISH_VERSION = "english|William Davidson Edition - English"


def _clean(html_text):
    if not html_text:
        return ""
    return strip_tags(html_text).strip()


def _segment_ref(daf_ref, index):
    return f"{daf_ref}:{index + 1}"


def _parse_gemara(daf_ref, davidson_text_data, links_data):
    segments_en = []
    if davidson_text_data:
        versions = davidson_text_data.get("versions") or []
        if versions:
            segments_en = versions[0].get("text") or []

    steinsaltz_he_by_ref = {}
    for link in links_data or []:
        if (link.get("collectiveTitle") or {}).get("en") != STEINSALTZ_TITLE:
            continue
        anchor_ref = link.get("anchorRef")
        he = _clean(link.get("he"))
        if anchor_ref and he:
            steinsaltz_he_by_ref.setdefault(anchor_ref, []).append(he)

    num_segments = max(len(segments_en), len(steinsaltz_he_by_ref))
    gemara = []
    for i in range(num_segments):
        ref = _segment_ref(daf_ref, i)
        en = _clean(segments_en[i]) if i < len(segments_en) else ""
        he = " ".join(steinsaltz_he_by_ref.get(ref, []))
        if en or he:
            gemara.append({"ref": ref, "en": en, "he": he})
    return gemara


def _parse_link(link):
    return {
        "ref": link.get("sourceRef"),
        "he_ref": link.get("sourceHeRef"),
        "anchor_ref": link.get("anchorRef"),
        "commentator": (link.get("collectiveTitle") or {}).get("en", ""),
        "he": _clean(link.get("he")),
        "en": _clean(link.get("text")),
    }


def parse_daf_context(daf_ref, davidson_text_data, links_data):
    gemara = _parse_gemara(daf_ref, davidson_text_data, links_data)

    rashi, mishnah, halacha, other_commentaries, links = [], [], [], [], []

    for link in links_data or []:
        parsed = _parse_link(link)
        if not (parsed["he"] or parsed["en"]):
            continue

        collective_title = parsed["commentator"]
        category = link.get("category")

        if collective_title in (RASHI_TITLE, STEINSALTZ_TITLE):
            # Steinsaltz already consumed into "gemara" above.
            if collective_title == RASHI_TITLE:
                rashi.append(parsed)
        elif category == "Mishnah":
            mishnah.append(parsed)
        elif category == "Halakhah":
            halacha.append(parsed)
        elif category == "Commentary":
            other_commentaries.append(parsed)
        else:
            links.append(parsed)

    return {
        "gemara": gemara,
        "rashi": rashi,
        "tosafot": [],  # populated by builder.py from dafyomi.co.il
        "insights": [],  # populated by builder.py from dafyomi.co.il
        "halacha_topics": [],  # populated by builder.py from dafyomi.co.il
        "vocabulary": [],  # populated by builder.py from dafyomi.co.il
        "mishnah": mishnah,
        "halacha": halacha,
        "other_commentaries": other_commentaries,
        "links": links,
        "metadata": {
            "ref": (davidson_text_data or {}).get("ref", daf_ref),
            "he_ref": (davidson_text_data or {}).get("heRef", ""),
            "primary_category": (davidson_text_data or {}).get("primary_category", ""),
        },
    }
