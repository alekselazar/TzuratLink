"""
Cache-first client for dafyomi.co.il's per-daf study APIs (Kollel Iyun
Hadaf), used to source several context sections that are far more usable as
LLM context than raw Sefaria text:

- tosfos    -> "tosafot" section (point-by-point Tosafot summary, He + En)
- insites   -> "insights" section ("explanation"/"general" branches)
- halachah  -> "halacha_topics" section (Gemara -> Rishonim -> Poskim, ready
               structured for the halacha branch)
- backgrnd  -> "vocabulary" section (the glossary half of this endpoint;
               its "Girsa" textual-variants half isn't parsed — low value)

Not every tractate/daf has coverage for every endpoint (e.g. Tamid/Meilah
Tosafot is sparse/absent) — that's a real content gap, not an error, so a
missing result just yields an empty list rather than raising.
"""
import json
import logging
import re
import urllib.request

from django.core.cache import cache
from django.utils.html import strip_tags
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

_SUCCESS_TTL = 60 * 60 * 24 * 30  # 30 days
_FAILURE_TTL = 60 * 60  # 1 hour
_SENTINEL = object()

_DAF_REF_RE = re.compile(r"^(.+?)\s+(\d+)[ab]?$")
_LEVEL_CLASS_RE = re.compile(r"^indent(\d+)(heb)?$")

# dafyomi.co.il tractate slugs, verified against the live site. Keys match
# the canonical English tractate names used elsewhere in the app (see
# node/components/TalmudData.js). Single-word tractates lowercase their
# Ashkenazi name (e.g. "Berakhot" -> "berachos"); two-word tractates use the
# first letter of the first word + the second word (e.g. "Bava Kamma" ->
# "bkama", "Rosh Hashanah" -> "rhashanah").
TRACTATE_SLUGS = {
    "Berakhot": "berachos",
    "Shabbat": "shabbos",
    "Eruvin": "eruvin",
    "Pesachim": "pesachim",
    "Shekalim": "shekalim",
    "Yoma": "yoma",
    "Sukkah": "sukah",
    "Beitzah": "beitzah",
    "Rosh Hashanah": "rhashanah",
    "Taanit": "taanis",
    "Megillah": "megilah",
    "Moed Katan": "mkatan",
    "Chagigah": "chagigah",
    "Yevamot": "yevamos",
    "Ketubot": "kesuvos",
    "Nedarim": "nedarim",
    "Nazir": "nazir",
    "Sotah": "sotah",
    "Gittin": "gitin",
    "Kiddushin": "kidushin",
    "Bava Kamma": "bkama",
    "Bava Metzia": "bmetzia",
    "Bava Batra": "bbasra",
    "Sanhedrin": "sanhedrin",
    "Makkot": "makos",
    "Shevuot": "shevuos",
    "Avodah Zarah": "azarah",
    "Horayot": "horayos",
    "Zevachim": "zevachim",
    "Menachot": "menachos",
    "Chullin": "chulin",
    "Bekhorot": "bechoros",
    "Arakhin": "erchin",
    "Temurah": "temurah",
    "Keritot": "kerisus",
    "Meilah": "meilah",
    "Tamid": "tamid",
    "Niddah": "nidah",
}


def _clean(text):
    if not text:
        return ""
    return strip_tags(text).strip()


def _resolve_daf_ref(daf_ref):
    """'Berakhot 2a' -> ('berachos', '2'). Raises ValueError if unmapped/unparseable."""
    match = _DAF_REF_RE.match((daf_ref or "").strip())
    if not match:
        raise ValueError(f"Cannot parse daf_ref: {daf_ref!r}")
    tractate, daf_number = match.group(1), match.group(2)
    slug = TRACTATE_SLUGS.get(tractate)
    if not slug:
        raise ValueError(f"No dafyomi.co.il slug mapped for tractate {tractate!r}")
    return slug, daf_number


def _fetch_endpoint_html(endpoint, daf_ref):
    """
    Returns the raw HTML fragment for a dafyomi.co.il API endpoint
    (tosfos/insites/halachah/backgrnd) + daf, or None if unavailable / not
    covered / tractate unmapped.
    """
    try:
        slug, daf_number = _resolve_daf_ref(daf_ref)
    except ValueError:
        logger.warning("dafyomi.co.il: cannot resolve daf_ref %r", daf_ref, exc_info=True)
        return None

    cache_key = f"dafyomi:{endpoint}:{slug}:{daf_number}"
    cached = cache.get(cache_key, _SENTINEL)
    if cached is not _SENTINEL:
        return cached

    url = f"https://www.dafyomi.co.il/api/{endpoint}/{slug}/{daf_number}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "TzuratLink/1.0"})
        with urllib.request.urlopen(req, timeout=8) as response:
            data = json.loads(response.read().decode("utf-8"))
        html = data.get("content") if data.get("status") == 200 else None
        cache.set(cache_key, html, _SUCCESS_TTL)
        return html
    except Exception:
        logger.warning("dafyomi.co.il fetch failed for %s", url, exc_info=True)
        cache.set(cache_key, None, _FAILURE_TTL)
        return None


def fetch_tosfos_html(daf_ref):
    return _fetch_endpoint_html("tosfos", daf_ref)


def _entry_text_and_type(p_tag):
    """Pulls the '<cl> Question:' label out of a <p>, returning (type, remaining text)."""
    if p_tag is None:
        return "", ""
    cl_span = p_tag.find("span", class_="cl")
    entry_type = ""
    if cl_span:
        entry_type = _clean(cl_span.get_text()).rstrip(":")
        cl_span.extract()
    return entry_type, _clean(p_tag.get_text())


def parse_tosfos_points(html):
    """
    Parses dafyomi.co.il's Tosafot summary fragment (a flat sequence of
    sibling divs, not real DOM nesting — class names like "indent2" only
    convey visual/logical nesting level) into a list of points:

    [{"subject_en": ..., "subject_he": ..., "summary": ..., "entries": [
        {"level": 1, "label": "(a)", "type": "Question", "he": ..., "en": ...},
        ...
    ]}]
    """
    if not html:
        return []

    soup = BeautifulSoup(html, "html.parser")
    points = []
    current = None
    pending_he = {}  # level -> he text, waiting for its paired indent{level} div

    for div in soup.find_all("div"):
        classes = div.get("class") or []
        cls = classes[0] if classes else ""
        p = div.find("p")

        if cls == "subject":
            if current:
                points.append(current)
            current = {
                "subject_en": _clean(p.get_text()) if p else "",
                "subject_he": "",
                "summary": "",
                "entries": [],
            }
            pending_he = {}
        elif current is None:
            continue
        elif cls == "subjectheb":
            current["subject_he"] = _clean(p.get_text()) if p else ""
        elif cls == "summary":
            label_span = p.find("span") if p else None
            if label_span:
                label_span.extract()
            text = _clean(p.get_text()) if p else ""
            current["summary"] = text.strip("()").strip()
        else:
            match = _LEVEL_CLASS_RE.match(cls)
            if not match:
                continue
            level = int(match.group(1))
            if match.group(2):  # ...heb
                pending_he[level] = _clean(p.get_text()) if p else ""
            else:
                label_el = div.find("span", class_="nm")
                label = _clean(label_el.get_text()) if label_el else ""
                entry_type, text = _entry_text_and_type(p)
                current["entries"].append({
                    "level": level,
                    "label": label,
                    "type": entry_type,
                    "he": pending_he.pop(level, ""),
                    "en": text,
                })

    if current:
        points.append(current)

    return points


def fetch_tosfos_points(daf_ref):
    """Fetch + parse in one call: the "tosafot" context section for a daf_ref."""
    return parse_tosfos_points(fetch_tosfos_html(daf_ref))


def parse_insights_points(html):
    """
    Parses dafyomi.co.il's "Insights into the Daily Daf" fragment (broader
    Q&A discussion of the sugya, not limited to Tosafot) into a list of
    points:

    [{"subject": ..., "entries": [
        {"label": "(a)", "kind": "reg", "text": "QUESTION: ..."}, ...
    ]}]

    Unlike Tosafot, type labels here ("QUESTION:"/"OPINIONS:"/"HALACHAH:")
    aren't in a separately-classed span, so they're left inline in the text
    rather than split out.
    """
    if not html:
        return []

    soup = BeautifulSoup(html, "html.parser")
    points = []
    current = None

    for div in soup.find_all("div"):
        classes = div.get("class") or []
        cls = classes[0] if classes else ""

        if cls == "subject":
            if current:
                points.append(current)
            nm = div.find("span", class_="nm")
            if nm:
                nm.extract()
            current = {"subject": _clean(div.get_text()), "entries": []}
        elif current is None:
            continue
        elif cls in ("reg", "reghal", "regoneword"):
            nm = div.find("span", class_="nm")
            label = ""
            if nm:
                label = _clean(nm.get_text())
                nm.extract()
            text = _clean(div.get_text())
            if text:
                current["entries"].append({"label": label, "kind": cls, "text": text})

    if current:
        points.append(current)

    return points


def fetch_insights_points(daf_ref):
    """Fetch + parse in one call: the "insights" context section for a daf_ref."""
    return parse_insights_points(_fetch_endpoint_html("insites", daf_ref))


def parse_halacha_topics(html):
    """
    Parses dafyomi.co.il's Halachah summary fragment (same flat indent1/2/3
    div structure as Tosafot, but English-only, with each topic organized
    into Gemara -> Rishonim -> Poskim sub-sections, plus a "See Also" list)
    into a list of topics:

    [{"subject": ..., "entries": [
        {"level": 1, "label": "(a)", "type": "", "text": "Gemara"},
        {"level": 2, "label": "1.", "type": "Mishnah", "text": "..."}, ...
    ], "see_also": ["..."]}]
    """
    if not html:
        return []

    soup = BeautifulSoup(html, "html.parser")
    topics = []
    current = None

    for div in soup.find_all("div"):
        classes = div.get("class") or []
        cls = classes[0] if classes else ""
        p = div.find("p")

        if cls == "subject":
            if current:
                topics.append(current)
            if p:
                idx_span = p.find("span", class_="indexentry")
                if idx_span:
                    idx_span.extract()
            current = {"subject": _clean(p.get_text()) if p else "", "entries": [], "see_also": []}
        elif current is None:
            continue
        elif cls == "seealso":
            continue
        elif cls == "seealsotext":
            current["see_also"].append(_clean(div.get_text()))
        else:
            match = _LEVEL_CLASS_RE.match(cls)
            if not match:
                continue
            level = int(match.group(1))
            label_el = div.find("span", class_="nm")
            label = _clean(label_el.get_text()) if label_el else ""
            entry_type, text = _entry_text_and_type(p)
            current["entries"].append({
                "level": level,
                "label": label,
                "type": entry_type,
                "text": text,
            })

    if current:
        topics.append(current)

    return topics


def fetch_halacha_topics(daf_ref):
    """Fetch + parse in one call: the "halacha_topics" context section for a daf_ref."""
    return parse_halacha_topics(_fetch_endpoint_html("halachah", daf_ref))


_GLOSSARY_SKIP_CLASSES = {
    "girsasep", "girsatext", "girsaloc", "girsalocheb", "girsa", "girsa1",
    "linecount", "spacer", "bbbline", "hybsub", "hyb", "pasuksource",
}


def parse_vocabulary_terms(html):
    """
    Parses the glossary half of dafyomi.co.il's Background fragment (the
    "Girsa"/textual-variants half is skipped — low value as LLM context)
    into a list of terms, each keyed to a specific line on the daf:

    [{"line": "[line 2]", "term_he": "...",
      "definition": "KORIN ES SHEMA (KERI'AS SHEMA)",
      "points": [{"label": "(a)", "text": "..."}]}]

    The site inconsistently wraps the transliterated term in its own span
    (some entries, e.g. simple one-liners, leave it as bare text), so term
    and gloss aren't split into separate fields — just one "definition".
    """
    if not html:
        return []

    soup = BeautifulSoup(html, "html.parser")
    terms = []
    current = None

    for p in soup.find_all("p"):
        classes = p.get("class") or []
        if not classes or classes[0] in _GLOSSARY_SKIP_CLASSES or "def" not in classes:
            continue

        if p.get("id"):
            if current:
                terms.append(current)
            nm = p.find("span", class_="nm")
            ln = p.find("span", class_="ln")
            defheb = p.find("span", class_="defheb")
            line = _clean(ln.get_text()) if ln else ""
            term_he = _clean(defheb.get_text()) if defheb else ""
            for span in (nm, ln, defheb, p.find("span", class_="hack")):
                if span:
                    span.extract()
            definition = _clean(p.get_text()).lstrip("-").strip()
            current = {"line": line, "term_he": term_he, "definition": definition, "points": []}
        elif current is not None:
            label_el = p.find("span", class_="nm")
            label = ""
            if label_el:
                label = _clean(label_el.get_text())
                label_el.extract()
            text = _clean(p.get_text())
            if text:
                current["points"].append({"label": label, "text": text})

    if current:
        terms.append(current)

    return terms


def fetch_vocabulary_terms(daf_ref):
    """Fetch + parse in one call: the "vocabulary" context section for a daf_ref."""
    return parse_vocabulary_terms(_fetch_endpoint_html("backgrnd", daf_ref))
