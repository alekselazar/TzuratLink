"""
Per-intent context section selection — each LLM prompt only receives the
sections relevant to its branch, not the entire daf context.
"""

INTENT_CONTEXT_MAP = {
    "summary": ["gemara", "rashi", "tosafot", "insights"],
    "explanation": ["gemara", "rashi", "tosafot", "insights"],
    "translation": ["gemara"],
    "rishonim": ["gemara", "rashi", "tosafot", "other_commentaries", "halacha_topics"],
    "halacha": ["gemara", "halacha", "halacha_topics"],
    "sources": ["gemara", "links", "halacha_topics"],
    "vocabulary": ["gemara", "vocabulary"],
    "quiz": ["gemara", "rashi", "tosafot", "insights", "vocabulary"],
    "general": ["gemara", "rashi", "tosafot", "insights"],
}


def select_context(full_context, intent):
    sections = INTENT_CONTEXT_MAP.get(intent, INTENT_CONTEXT_MAP["general"])
    selected = {key: full_context.get(key, []) for key in sections}
    selected["metadata"] = full_context.get("metadata", {})
    return selected
