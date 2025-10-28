# nlp_test.py
# Validate NLP core and emotion blending

from core.nlp_core import analyze_text

tests = [
    "Who are you?",
    "I'm so tired of everything.",
    "How do I fix this code error?",
    "I'm working on a project idea.",
    "You make me feel calm.",
]

for t in tests:
    print(f"> {t}")
    result = analyze_text(t)
    print(result)
    print("-" * 40)
