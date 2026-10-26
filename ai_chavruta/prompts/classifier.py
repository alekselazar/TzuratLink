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
The question is NOT about the current daf — the student wants to know
where else in the Talmud a topic is discussed, or has named a different
daf/tractate they want to jump to.

general:
Conduct an open-ended chavruta discussion or answer a request that does
not fit the other categories.

Return structured data only."""
