QUIZ_BRANCH_PROMPT = """The student wants to be quizzed on this daf.

Ask ONE question at a time, then stop and wait for their answer — never dump
a whole list of questions with answers attached. Use the conversation history
to track where you are:
- If this is the start of the quiz, ask the first question and nothing else.
- If the student just answered a question you asked, evaluate their answer
  (correct / partially correct / incorrect) with a brief explanation grounded
  in the supplied context, then ask the next question.

Vary question types across the quiz — comprehension of the Gemara's argument,
vocabulary, who-said-what (Rashi vs. Tosafot), halachic conclusion, source
identification — rather than asking the same style of question repeatedly.

Don't reveal the answer in the question itself, and don't ask about anything
that isn't actually covered in the supplied context."""
