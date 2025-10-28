"""
Adapter to map EntityAwarenessPipeline.analyze(...) -> detect_intent(...) shaped output
expected by Sagira's EmotionEngine usage.
"""
from typing import Dict, Any

try:
    from src.entity_awareness import EntityAwarenessPipeline
    from src.memory import InMemoryConversationMemory
except Exception:
    # allow importing when run from project root
    from entity_awareness import EntityAwarenessPipeline  # type: ignore
    from memory import InMemoryConversationMemory  # type: ignore

# Fallback core analysis
from core.nlp_core import analyze_text

class EAAdapter:
    def __init__(self, **kwargs):
        # Create pipeline; if heavy models missing, pipeline will fallback
        # Ensure a default in-process coref resolver is used unless overridden
        if 'llm_coref_resolver' not in kwargs:
            try:
                from src.coref_resolver import simple_coref_resolver
            except Exception:
                try:
                    from coref_resolver import simple_coref_resolver  # type: ignore
                except Exception:
                    simple_coref_resolver = None
            if simple_coref_resolver:
                kwargs['llm_coref_resolver'] = simple_coref_resolver

        try:
            self.pipeline = EntityAwarenessPipeline(**kwargs)
        except Exception:
            self.pipeline = None

    def detect_intent(self, text: str) -> Dict[str, Any]:
        if self.pipeline:
            enriched = self.pipeline.analyze(text)
            intent = None
            if enriched.get('intents'):
                # zero-shot output shape may vary
                i = enriched['intents']
                if isinstance(i, dict) and 'labels' in i:
                    intent = i['labels'][0]
            if not intent:
                # fallback to core analyzer
                core = analyze_text(text)
                intent = core.get('intent_guess')
                sentiment = core.get('sentiment', 0.0)
            else:
                # try to derive sentiment from pipeline
                if isinstance(enriched.get('sentiment'), dict):
                    sentiment = enriched['sentiment'].get('score', 0.0)
                else:
                    sentiment = 0.0

            # derive mood similar to EmotionEngine.derive_mood_from_analysis
            if intent == 'emotional_state':
                if sentiment < -0.2:
                    mood = 'depressed'
                elif sentiment > 0.2:
                    mood = 'creative'
                else:
                    mood = 'neutral'
            elif intent == 'productivity':
                mood = 'anxious' if sentiment < 0 else 'neutral'
            else:
                # keyword-based fallback
                keywords = analyze_text(text).get('keywords', [])
                if any(k in ['tired', 'exhausted', 'drained'] for k in keywords):
                    mood = 'depressed'
                elif any(k in ['creative', 'inspired', 'idea'] for k in keywords):
                    mood = 'creative'
                elif any(k in ['worried', 'anxious', 'stuck'] for k in keywords):
                    mood = 'anxious'
                else:
                    mood = 'neutral'

            tone = 'soothing' if sentiment < -0.2 else ('energized' if sentiment > 0.2 else 'neutral')
            keywords = analyze_text(text).get('keywords', [])

            return {"intent": intent, "sentiment": sentiment, "mood": mood, "tone": tone, "keywords": keywords}

        # final fallback
        core = analyze_text(text)
        intent = core.get('intent_guess')
        sentiment = core.get('sentiment', 0.0)
        # simple mood mapping
        if intent == 'emotional_state':
            mood = 'depressed' if sentiment < -0.2 else ('creative' if sentiment > 0.2 else 'neutral')
        else:
            mood = 'neutral'
        return {"intent": intent, "sentiment": sentiment, "mood": mood, "tone": 'neutral', "keywords": core.get('keywords', [])}
