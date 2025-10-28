# nlp_core.py
# Sagira v0.3.2 - Semantic Infusion Patch
# Natural Language Preprocessor for intent and sentiment interpretation

import re
from textblob import TextBlob
from nltk.tokenize import word_tokenize

# Basic intent inference logic
def infer_intent(tokens):
    tokens = [t.lower() for t in tokens]

    # Enhanced identity query detection
    if ("you" in tokens and any(x in tokens for x in ["who", "what"])):
        return "identity_query"
    if ("your" in tokens and any(x in tokens for x in ["name", "identity", "introduce"])):
        return "identity_query"

    # Purpose / role queries
    if any(x in tokens for x in ["what", "why", "purpose", "role", "function", "doing"]):
        return "purpose_query"

    # Enhanced emotional state detection
    if any(x in tokens for x in ["feel", "feeling", "emotion", "mood", "state"]):
        return "emotional_state"
    if any(x in tokens for x in ["sad", "happy", "anxious", "tired", "angry", "frustrated",
                               "worried", "excited", "confused", "stressed", "overwhelmed"]):
        return "emotional_state"

    # Productivity / task related
    if any(x in tokens for x in ["project", "work", "build", "code"]):
        return "productivity"

    # Assistance/help
    if any(x in tokens for x in ["help", "how", "fix", "error"]):
        return "assistance"

    return "general_chat"

# Analyze raw input for semantics + affective tone
def analyze_text(user_input):
    if not user_input.strip():
        return {"intent_guess": "empty", "sentiment": 0.0, "keywords": []}

    blob = TextBlob(user_input)
    sentiment = blob.sentiment.polarity  # -1 to +1
    tokens = word_tokenize(user_input.lower())
    intent = infer_intent(tokens)

    return {
        "intent_guess": intent,
        "sentiment": sentiment,
        "keywords": tokens
    }

if __name__ == "__main__":
    # Debug quick test
    text = input("Test input: ")
    print(analyze_text(text))
