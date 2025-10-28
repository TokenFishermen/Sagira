"""
Entity awareness enrichment pipeline with safe fallbacks.
This implementation will try to load spaCy, sentence-transformers and transformers.
If unavailable, it falls back to the existing `core.nlp_core.analyze_text` to provide intent/sentiment/keywords so integration tests can run without heavy downloads.
"""
from typing import Optional, List, Dict, Any
import numpy as np

# Lightweight fallback imports
try:
    import spacy
    from transformers import pipeline
    from sentence_transformers import SentenceTransformer
    _HAVE_FULL = True
except Exception:
    _HAVE_FULL = False

# Import local memory helper
try:
    from src.memory import InMemoryConversationMemory, KBIndex
except Exception:
    # When running inside project, import from top-level package
    from memory import InMemoryConversationMemory, KBIndex  # type: ignore

# Fallback to project's nlp_core
from core.nlp_core import analyze_text

class EntityAwarenessPipeline:
    def __init__(
        self,
        *,
        spacy_model: str = "en_core_web_trf",
        embed_model: str = "all-MiniLM-L6-v2",
        sentiment_model: str = "distilbert-base-uncased-finetuned-sst-2-english",
        zero_shot_model: str = "facebook/bart-large-mnli",
        kb_index: Optional[KBIndex] = None,
        memory: Optional[InMemoryConversationMemory] = None,
        llm_coref_resolver=None,
    ):
        self.kb_index = kb_index
        self.llm_coref_resolver = llm_coref_resolver

        if _HAVE_FULL:
            # spaCy NER
            try:
                self.nlp = spacy.load(spacy_model)
            except Exception:
                # fallback to blank model
                self.nlp = spacy.blank("en")
            # embeddings
            try:
                self.embedder = SentenceTransformer(embed_model)
            except Exception:
                self.embedder = None
            # sentiment
            try:
                self.sentiment = pipeline("sentiment-analysis", model=sentiment_model)
            except Exception:
                self.sentiment = None
            # zero-shot
            try:
                self.zero_shot = pipeline("zero-shot-classification", model=zero_shot_model)
            except Exception:
                self.zero_shot = None
        else:
            # Minimal fallback objects
            self.nlp = None
            self.embedder = None
            self.sentiment = None
            self.zero_shot = None

        self.memory = memory or InMemoryConversationMemory(self.embedder)

    def _extract_entities(self, text: str) -> List[Dict[str, Any]]:
        if not self.nlp:
            # fallback: very small heuristic using capitalization
            ents = []
            tokens = text.split()
            for i, t in enumerate(tokens):
                if t.istitle() and len(t) > 1:
                    ents.append({"text": t, "label": "PROPER", "start": text.find(t), "end": text.find(t) + len(t)})
            return ents
        doc = self.nlp(text)
        ents = []
        for ent in doc.ents:
            ents.append({"text": ent.text, "label": ent.label_, "start": ent.start_char, "end": ent.end_char})
        return ents

    def _embed(self, texts: List[str]):
        if self.embedder is None:
            # fallback to dummy vectors (hash-based)
            vecs = []
            for t in texts:
                h = abs(hash(t)) % 10000
                v = np.ones(32) * (h / 10000.0)
                vecs.append(v)
            return np.array(vecs)
        return np.array(self.embedder.encode(texts, convert_to_numpy=True))

    def _intent_and_slots(self, text: str, candidate_labels: List[str]):
        if not self.zero_shot:
            # fallback: use analyze_text.intent_guess
            analysis = analyze_text(text)
            return {"labels": [analysis["intent_guess"]], "scores": [1.0], "sequence": text}
        return self.zero_shot(text, candidate_labels)

    def analyze(self, text: str, conversation_history: Optional[List[Dict]] = None, intent_labels: Optional[List[str]] = None) -> Dict[str, Any]:
        # 1. Coreference resolution (if resolver provided)
        resolved = text
        if self.llm_coref_resolver:
            try:
                resolved = self.llm_coref_resolver(text, conversation_history)
            except Exception:
                resolved = text

        # 2. NER
        entities = self._extract_entities(resolved)

        # 3. Sentiment
        if self.sentiment:
            sentiment = self.sentiment(resolved)[0]
        else:
            analysis = analyze_text(resolved)
            sentiment = {"label": "neutral", "score": analysis.get("sentiment", 0.0)}

        # 4. Embeddings
        text_embedding = self._embed([resolved])[0]
        entity_texts = [e["text"] for e in entities] if entities else [resolved]
        entity_embeddings = self._embed(entity_texts)

        # 5. Intent (optional)
        intents = None
        if intent_labels:
            intents = self._intent_and_slots(resolved, intent_labels)

        # 6. KB linking
        kb_matches = []
        if self.kb_index and entities:
            for e_text, e_embed in zip(entity_texts, entity_embeddings):
                matches = self.kb_index.search_by_embedding(e_embed, top_k=4)
                kb_matches.append({"entity": e_text, "matches": matches})

        # 7. Memory retrieval
        memory_relevant = []
        try:
            memory_relevant = self.memory.find_relevant(text_embedding, top_k=5)
        except Exception:
            memory_relevant = []

        # 8. Save to memory
        try:
            self.memory.add_message({"text": resolved, "entities": entities, "embedding": text_embedding.tolist()})
        except Exception:
            pass

        return {
            "original_text": text,
            "resolved_text": resolved,
            "entities": entities,
            "sentiment": sentiment,
            "intents": intents,
            "text_embedding": text_embedding,
            "entity_embeddings": entity_embeddings,
            "kb_matches": kb_matches,
            "memory_relevant": memory_relevant,
        }
