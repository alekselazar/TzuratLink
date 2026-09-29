"""
Assembles and caches the full structured context for a daf: Gemara
(Steinsaltz Hebrew + Davidson English) + Rashi/Mishnah/Halakhah/other
commentaries from Sefaria, and Tosafot from dafyomi.co.il. Caches the
combined result so repeated chat messages about the same daf skip
re-fetching and re-parsing entirely.
"""
from core.sefaria import get_text_v3, get_links

from ..cache.context_cache import get_cached_context, set_cached_context
from .dafyomi_client import (
    fetch_halacha_topics,
    fetch_insights_points,
    fetch_tosfos_points,
    fetch_vocabulary_terms,
)
from .parser import DAVIDSON_ENGLISH_VERSION, parse_daf_context


def build_daf_context(daf_ref):
    cached = get_cached_context(daf_ref)
    if cached is not None:
        return cached

    davidson_text_data = get_text_v3(daf_ref, version=DAVIDSON_ENGLISH_VERSION)
    links_data = get_links(daf_ref)

    context = parse_daf_context(daf_ref, davidson_text_data, links_data)
    context["tosafot"] = fetch_tosfos_points(daf_ref)
    context["insights"] = fetch_insights_points(daf_ref)
    context["halacha_topics"] = fetch_halacha_topics(daf_ref)
    context["vocabulary"] = fetch_vocabulary_terms(daf_ref)

    set_cached_context(daf_ref, context)
    return context
