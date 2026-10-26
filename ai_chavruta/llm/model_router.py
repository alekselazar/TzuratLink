"""Maps an intent to the model tier that should answer it."""
from .factory import get_chat_model, get_reasoning_model

# These branches need real multi-source synthesis — comparing Rishonim's
# positions, tracing a halachic ruling through Gemara -> Rishonim -> Poskim —
# not just restating/organizing material already in the context.
_REASONING_INTENTS = {"halacha", "rishonim"}


def get_model_for_intent(intent, temperature=0.2):
    if intent in _REASONING_INTENTS:
        return get_reasoning_model(temperature=temperature)
    return get_chat_model(temperature=temperature)
