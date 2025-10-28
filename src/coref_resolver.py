"""
Lightweight in-process coreference resolver.

This is a heuristic resolver intended to be fast and dependency-free.
It attempts to replace pronouns (it/they/he/she/them/its/their) with the most
recent named entity or noun phrase found in the conversation history.

It's not perfect but improves handling of short dialogs for entity-awareness
without calling an external LLM. You can replace this with an LLM-based
resolver later by implementing the same function signature.
"""
import re
from typing import List, Dict

PRONOUN_PATTERNS = [
    (re.compile(r"\b(it|its)\b", re.I), "it"),
    (re.compile(r"\b(they|them|their|theirs)\b", re.I), "they"),
    (re.compile(r"\b(he|him|his)\b", re.I), "he"),
    (re.compile(r"\b(she|her|hers)\b", re.I), "she"),
]


def _extract_candidates_from_history(conversation_history: List[Dict]) -> List[str]:
    """Return a list of candidate entity strings from conversation history,
    most recent first."""
    candidates = []
    if not conversation_history:
        return candidates
    # Look at recent messages (last 8)
    # small stoplist of common verbs/auxiliary words to avoid as candidates
    stop_verbs = set(["arrived", "bought", "bought", "help", "return", "sent", "received", "got", "was", "is", "are", "be", "have", "had"])
    for msg in reversed(conversation_history[-8:]):
        text = msg.get("text", "")
        # Prefer nouns following articles ("the lens", "a camera")
        article_nouns = re.findall(r"\b(?:a|an|the)\s+([A-Za-z][a-z0-9-]+)\b", text, flags=re.I)
        for an in article_nouns:
            if an.lower() not in [x.lower() for x in candidates]:
                candidates.append(an)

        # Find sequences of capitalized words (simple proper-noun heuristic)
        caps = re.findall(r"\b([A-Z][a-z0-9]+(?:\s+[A-Z][a-z0-9]+)*)\b", text)
        for c in caps:
            if c.lower() not in [x.lower() for x in candidates]:
                candidates.append(c)
        # Also consider quoted phrases
        quotes = re.findall(r'"([^"]+)"', text)
        for q in quotes:
            if q.lower() not in [x.lower() for x in candidates]:
                candidates.append(q)
        # Fallback: last noun-like token that isn't a common verb
        tokens = re.findall(r"\b([a-zA-Z][a-z]+)\b", text)
        if tokens:
            # walk tokens from the end to find a non-verb candidate
            for t in reversed(tokens):
                if t.lower() in stop_verbs:
                    continue
                if t.lower() not in [x.lower() for x in candidates]:
                    candidates.append(t)
                    break
    return candidates


def simple_coref_resolver(text: str, conversation_history: List[Dict]) -> str:
    """Resolve simple pronouns in `text` using `conversation_history`.

    This replaces pronouns with the most likely recent entity candidate.
    It's conservative: if no candidate is found, it returns the original text.
    """
    if not text or not conversation_history:
        return text

    candidates = _extract_candidates_from_history(conversation_history)
    if not candidates:
        return text

    # Choose the top candidate (most recent)
    target = candidates[0]

    resolved = text
    # Replace pronouns with the candidate; do longer pronouns first
    for pattern, label in PRONOUN_PATTERNS:
        # Use a simple replacement; preserve capitalization of the match
        def _repl(m):
            matched = m.group(0)
            # Preserve casing: if matched was title-case, title the target
            if matched[0].isupper():
                return target
            else:
                return target.lower()

        resolved = pattern.sub(_repl, resolved)

    # If replacements produced duplicated words ("camera camera"), collapse them
    resolved = re.sub(r"\b(\w+)(\s+\1\b)+", r"\1", resolved, flags=re.I)
    return resolved
