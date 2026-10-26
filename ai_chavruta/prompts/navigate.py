NAVIGATE_BRANCH_PROMPT = """The student is asking about something that isn't on the daf they currently
have open — they want to know where else in the Talmud a topic is
discussed, or they've named a different daf they want to jump to.

Below are candidate passages retrieved from a Shas-wide index, each with its
exact ref and a short summary. These are the ONLY places you may point the
student to — do not rely on your own memory of Shas, and do not invent or
suggest a ref that isn't listed below.

- If one of the candidates actually answers the question, call the
  select_daf tool with its exact ref.
- If none of the candidates fit, don't call the tool — tell the student
  honestly that you couldn't find where that's discussed.
- Keep your answer to a sentence or two — if you called the tool, the
  student will see a "go there" option, so you don't need to repeat the
  reference in full."""
