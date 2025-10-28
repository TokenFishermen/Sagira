# Integration Patch Plan: Semantic Layer into Sagira's Response Loop

## Objective

Integrate `nlp_core.analyze_text` into `main.py` and `emotion_engine.py` to replace regex-based mood detection with contextual NLP analysis. This will enable Sagira to respond based on intent, sentiment, and keywords, improving emotional resonance and humanization.

## Current State Analysis

- `main.py`: Uses `nlp_core.analyze_text` for intent and sentiment, but falls back to regex `detect_mood` for mood. Templates are selected based on mood, but not fully leveraging NLP.
- `emotion_engine.py`: Uses `analyze_text` in `detect_intent`, but response generation is template-based without dynamic adjustment.
- Gap: Mood is not derived from NLP; sentiment and intent are underutilized for tone and pacing.

## Proposed Changes

### 1. Update Mood Detection in `main.py`

- Replace `detect_mood(user_input)` with a function that maps `intent_guess` and `sentiment` to mood.
- Example mapping:
  - If `intent_guess` == 'emotional_state' and `sentiment` < -0.2: mood = 'depressed'
  - If `intent_guess` == 'emotional_state' and `sentiment` > 0.2: mood = 'creative'
  - If `intent_guess` == 'productivity' and `sentiment` < 0: mood = 'anxious'
  - Default: 'neutral'
- Remove or deprecate the old `detect_mood` function.

### 2. Enhance Emotion Engine in `emotion_engine.py`

- Modify `detect_intent` to return a dict with intent, sentiment, and derived mood.
- Update `blend_affective_trace` to use sentiment for blending weight (e.g., higher sentiment variance increases blending).
- Add a method to adjust tone based on sentiment (e.g., soothing for negative, energized for positive).

### 3. Dynamic Template Selection

- In `main.py`, select templates not just by mood, but by intent + sentiment.
- Expand `TEMPLATE_POOL` with sub-variants (e.g., anxious_positive, anxious_negative).
- Use keywords from analysis to personalize responses (e.g., reference specific words like "creative" or "anxious").

### 4. Humanization Adjustments

- In `polish_response` and `apply_personality_filter`, incorporate sentiment for pacing:
  - Negative sentiment: Add more ellipses and lowercase.
  - Positive sentiment: Add warmth or energy.
- Use intent to vary sentence length (e.g., short for 'identity_query', longer for 'emotional_state').

### 5. Memory Integration

- Store intent, sentiment, and keywords in `conversation_history` for context in future responses.
- Use keywords for better memory search relevance.

## Implementation Steps

1. Create a new function `derive_mood_from_analysis(analysis)` in `main.py`.
2. Update the chat loop in `main.py` to use derived mood.
3. Modify `emotion_engine.py` to return enhanced intent data.
4. Test with sample inputs to ensure mood mapping is accurate.
5. Run critical-path test: Input "I'm feeling creative but anxious." and verify response reflects mixed sentiment.

## Dependencies

- Ensure `textblob` and `nltk` are installed (already verified).
- No new files needed; edits to existing.

## Testing

- Unit test the mood derivation function.
- Integration test: Simulate dialogue and check if responses adapt to intent/sentiment.
- Live test: Run Sagira and input varied statements, observe resonance.

## Rollback Plan

- If issues arise, revert to old `detect_mood` by commenting out new code.
- Keep old function intact during transition.

## Next Steps

- Implement changes in order.
- Confirm with user before applying edits.
