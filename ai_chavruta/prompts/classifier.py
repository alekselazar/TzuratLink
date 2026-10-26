CLASSIFIER_PROMPT = """Classify the user's request for a Talmud-study assistant.

Available intents:

summary:
Summarize the daf, sugya, passage, or argument.

explanation:
Explain the reasoning, structure, hava amina, rejection, or conclusion.

translation:
Translate or paraphrase Hebrew or Aramaic text.

rishonim:
Compare or explain Rashi, Tosafot, or other commentators.

halacha:
Determine or explain a halachic conclusion or later ruling.

sources:
Locate citations, references, verses, parallels, or linked texts.

vocabulary:
Explain words, phrases, grammar, or terminology.

quiz:
Generate or continue a learning quiz.

navigate:
The question is about a topic that is NOT actually discussed on the
current daf — whether or not the student explicitly asks "where is this
discussed" or names a different daf. This includes substantive questions
about halacha, a sugya, or a concept that belongs elsewhere in Shas (e.g.
asking about found-object law on a daf about firstborn-animal blemishes).
Use this whenever answering well would require citing a source outside
the current daf's own content — never answer such a question from general
knowledge in the "general" branch; route it here so the answer is
grounded in an actual retrieved source instead of guessed.

general:
Open-ended chavruta discussion, small talk, or a request that doesn't fit
any other category AND doesn't require citing a specific source — e.g.
"let's discuss the themes of this daf" or a meta question about how to
study. If answering well would require citing a halachic source, ruling,
or specific text, use "navigate" or one of the daf-specific intents
instead, not "general".

Return structured data only."""
