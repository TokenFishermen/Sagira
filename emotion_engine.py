import time
import random
import json
import os
from typing import Optional
from core.nlp_core import analyze_text

class EmotionEngine:
    def __init__(self, memory_file="memory/sagira_memory.json", use_ea: Optional[bool] = None, ea_adapter=None):
        self.memory_file = memory_file
        self.current_mood = "neutral"
        self.tone = "steady"
        self.blending_weight = 0.2  # Affective trace blending weight (0.1-0.3)
        self.decay_factor = 0.8  # Resonance decay per exchange (fades after 3-5)
        self.exchange_count = 0
        # Optional EA adapter
        self.ea_adapter = ea_adapter
        # Determine whether to use EA: explicit arg > environment variable > default False
        if use_ea is None:
            env_val = os.getenv("SAGIRA_USE_EA", os.getenv("USE_EA", "false"))
            try:
                use_ea = str(env_val).strip().lower() in ("1", "true", "yes", "y")
            except Exception:
                use_ea = False

        if use_ea and not self.ea_adapter:
            try:
                from core.ea_adapter import EAAdapter
                self.ea_adapter = EAAdapter()
                print("[DEBUG] EmotionEngine: EAAdapter loaded")
            except Exception:
                self.ea_adapter = None
                print("[DEBUG] EmotionEngine: EAAdapter not available, falling back to internal analyzer")
        self.load_memory()

    def load_memory(self):
        try:
            with open(self.memory_file, "r") as f:
                memory = json.load(f)
                self.current_mood = memory.get("user_state", {}).get("mood", "neutral")
        except FileNotFoundError:
            self.current_mood = "neutral"

    def smooth_mood(self, new_mood):
        # Smooth transition between moods
        mood_transitions = {
            "neutral": {"anxious": "tense", "depressed": "somber", "creative": "inspired"},
            "anxious": {"neutral": "calming", "depressed": "overwhelmed"},
            "depressed": {"neutral": "steady", "creative": "reflective"},
            "creative": {"neutral": "focused", "anxious": "excited"}
        }
        self.tone = mood_transitions.get(self.current_mood, {}).get(new_mood, "steady")
        self.current_mood = new_mood
        return self.tone

    def simulate_delay(self, mood=None):
        # Simulate human-like response delay based on mood
        base_delay = 1.0
        mood_delays = {
            "anxious": 0.5,  # Quick, tense
            "depressed": 2.0,  # Slow, somber
            "creative": 1.5,  # Thoughtful
            "neutral": 1.0
        }
        delay = mood_delays.get(mood or self.current_mood, base_delay)
        delay += random.uniform(-0.2, 0.2)  # Add variability
        time.sleep(delay)

    def contextualize_phrase(self, phrase, mood=None):
        # Add emotional context to phrases
        mood_prefixes = {
            "anxious": "…quickly,",
            "depressed": "…slowly,",
            "creative": "…imaginatively,",
            "neutral": "…carefully,"
        }
        prefix = mood_prefixes.get(mood or self.current_mood, "…")
        return prefix + " " + phrase.lower()

    def detect_intent(self, text: str) -> dict:
        # If EA adapter present, prefer it (it returns the expected dict)
        if self.ea_adapter:
            try:
                if hasattr(self.ea_adapter, 'detect_intent'):
                    res = self.ea_adapter.detect_intent(text)
                    print(f"[DEBUG] EmotionEngine: EAAdapter returned: {res}")
                    return res
            except Exception as e:
                print(f"[DEBUG] EmotionEngine: EAAdapter failed: {e}")

        # Debug logging for pipeline tracing
        print(f"[DEBUG] EmotionEngine.detect_intent received: {text}")

        analysis = analyze_text(text)
        intent = analysis.get("intent_guess")
        sentiment = analysis.get("sentiment", 0.0)
        keywords = analysis.get("keywords", [])

        # Debug logging
        print(f"[DEBUG] Raw analysis - intent_guess: {intent}, sentiment: {sentiment}")
        print(f"[DEBUG] Keywords: {keywords}")

        # Derive mood from analysis
        mood = self.derive_mood_from_analysis(analysis)

        # Adjust tone based on sentiment (more sensitive)
        if sentiment < -0.2:
            tone = "soothing"
        elif sentiment > 0.2:
            tone = "energized"
        else:
            tone = "neutral"

        # Blend affective trace with sentiment variance
        sentiment_variance = abs(sentiment)
        self.blending_weight = min(0.3, sentiment_variance * 0.5)  # Adjust blending based on sentiment strength

        result = {
            "intent": intent,
            "sentiment": sentiment,
            "mood": mood,
            "tone": tone,
            "keywords": keywords
        }

        # Final debug output
        print(f"[DEBUG] EmotionEngine.detect_intent result: {result}")

        return result

    def derive_mood_from_analysis(self, analysis):
        intent = analysis["intent_guess"]
        sentiment = analysis["sentiment"]
        keywords = analysis["keywords"]

        # Mapping based on intent and sentiment
        if intent == "emotional_state":
            if sentiment < -0.2:
                return "depressed"
            elif sentiment > 0.2:
                return "creative"
            else:
                return "neutral"
        elif intent == "productivity":
            if sentiment < 0:
                return "anxious"
            else:
                return "neutral"
        elif intent == "identity_query":
            return "neutral"
        elif intent == "purpose_query":
            return "neutral"
        else:
            # Fallback to keywords
            if any(k in ["tired", "exhausted", "drained"] for k in keywords):
                return "depressed"
            elif any(k in ["creative", "inspired", "idea"] for k in keywords):
                return "creative"
            elif any(k in ["worried", "anxious", "stuck"] for k in keywords):
                return "anxious"
            else:
                return "neutral"

    def get_affective_trace(self):
        return {
            "mood": self.current_mood,
            "tone": self.tone,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(time.time()))
        }

    def blend_affective_trace(self, new_mood):
        # Blend previous affective trace with new mood for recursive memory
        previous_trace = self.get_affective_trace()
        blended_mood = self.blend_moods(previous_trace["mood"], new_mood)
        self.current_mood = blended_mood
        self.exchange_count += 1
        # Apply decay after 3-5 exchanges
        if self.exchange_count > 3:
            self.blending_weight *= self.decay_factor
        return blended_mood

    def blend_moods(self, prev_mood, new_mood):
        # Simple mood blending with weight
        if prev_mood == new_mood:
            return new_mood
        # Blend towards new mood with weight
        if random.random() < self.blending_weight:
            return new_mood
        return prev_mood

    def generate_template(self, intent, tone):
        """Generate a response using the response variation system."""
        from core.response_variation import pick_template

        # Use exchange_count as seed for deterministic but varying responses
        seed = self.exchange_count if hasattr(self, 'exchange_count') else None
        response = pick_template(intent, seed=seed)

        # Add tone tag if tone is significant
        tone_tag = {
            "soothing": " My tone softens, steady like water.",
            "energized": " There's a pulse of warmth in my response.",
            "neutral": ""
        }
        return response + tone_tag.get(tone, "")
