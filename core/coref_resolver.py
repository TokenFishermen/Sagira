import spacy
from typing import List, Dict, Any, Optional

# Load once globally
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    nlp = None
    print("[WARNING] spaCy model 'en_core_web_sm' not found. Using fallback heuristic resolver.")

def simple_coref_resolver(text: str, conversation_history: Optional[List[Dict[str, Any]]] = None) -> str:
    """
    Resolve basic pronouns and references using spaCy noun chunks.
    Falls back to heuristic resolution if spaCy is unavailable.

    Args:
        text: Input text to resolve references in
        conversation_history: List of previous conversation messages, each with "text" key

    Returns:
        Text with pronouns replaced with their referents where possible
    """
    if nlp is None:
        # Fallback heuristic: naive "it" -> last noun in conversation
        if conversation_history:
            last_text = conversation_history[-1].get("text", "")
            last_nouns = [tok for tok in last_text.split()
                         if tok.lower() not in ("it", "they", "them", "he", "she")]
            if "it" in text.lower() and last_nouns:
                text = text.replace("it", last_nouns[-1])
        return text

    doc = nlp(text)

    # Collect all noun chunks from conversation history
    context_nouns = []
    if conversation_history:
        for msg in conversation_history[::-1]:  # Most recent first
            c_doc = nlp(msg.get("text", ""))
            context_nouns.extend([
                chunk for chunk in c_doc.noun_chunks
                if not all(t.lower_ in ("it", "they", "them", "he", "she") for t in chunk)
            ])

    # Find pronouns that need resolution
    resolved_tokens = []
    for token in doc:
        if token.lower_ in ("it", "they", "them", "he", "she") and context_nouns:
            # Match gender/number if possible
            matched_noun = None
            for noun in context_nouns:
                # Enhanced gender detection using named entity recognition
                if token.lower_ in ("he", "she"):
                    noun_doc = nlp(" ".join(t.text for t in noun))
                    person_ents = [ent for ent in noun_doc.ents if ent.label_ == "PERSON"]

                    # Use name-based gender detection as backup
                    is_male_name = any(name in noun.text.lower() for name in ["john", "james", "robert", "michael"])
                    is_female_name = any(name in noun.text.lower() for name in ["sarah", "mary", "elizabeth", "jennifer"])

                    if person_ents and (
                        (token.lower_ == "he" and is_male_name) or
                        (token.lower_ == "she" and is_female_name)
                    ):
                        matched_noun = noun
                        break
                else:
                    # For "it" and "they", use number agreement
                    if token.lower_ in ("they", "them"):
                        # Check if noun is plural
                        is_plural = any(t.tag_ in ("NNS", "NNPS") for t in noun)
                        if is_plural:
                            matched_noun = noun
                            break
                    else:  # "it"
                        # Use first non-person noun
                        noun_doc = nlp(" ".join(t.text for t in noun))
                        if not any(ent.label_ == "PERSON" for ent in noun_doc.ents):
                            matched_noun = noun
                            break

            if matched_noun:
                resolved_tokens.append(matched_noun.text)
            else:
                resolved_tokens.append(token.text)
        else:
            resolved_tokens.append(token.text)

    return " ".join(resolved_tokens)

def get_conversation_entities(conversation_history: List[Dict[str, Any]]) -> List[str]:
    """
    Extract all entities from conversation history using spaCy.
    Useful for tracking what entities have been discussed.

    Args:
        conversation_history: List of conversation messages

    Returns:
        List of unique entity strings found in the conversation
    """
    if nlp is None:
        return []

    entities = set()
    for msg in conversation_history:
        doc = nlp(msg.get("text", ""))
        # Add named entities
        entities.update(ent.text for ent in doc.ents)
        # Add normalized noun chunks (without determiners)
        for chunk in doc.noun_chunks:
            # Skip pronouns
            if all(t.lower_ in ("it", "they", "them", "he", "she") for t in chunk):
                continue
            # Remove determiners and get root noun
            if chunk.root.head.pos_ == "ADP":  # Handle prepositional phrases
                clean_text = " ".join(t.text for t in chunk if t.pos_ not in ("DET", "PUNCT"))
            else:
                clean_text = chunk.root.text
            entities.add(clean_text)

    return sorted(entities)
