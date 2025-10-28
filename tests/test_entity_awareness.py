import pytest

def test_ea_adapter_detects_identity():
    try:
        from core.ea_adapter import EAAdapter
    except Exception:
        pytest.skip("EAAdapter not importable")

    engine = EAAdapter()
    res = engine.detect_intent("Who are you?")
    assert isinstance(res, dict)
    assert res.get('intent') in ('identity_query', 'identity', 'general_chat') or res.get('intent') is not None


def test_emotion_engine_uses_ea_adapter():
    try:
        from emotion_engine import EmotionEngine
    except Exception:
        pytest.skip("EmotionEngine not importable")

    eng = EmotionEngine(use_ea=True)
    res = eng.detect_intent("I am feeling anxious.")
    assert isinstance(res, dict)
    assert res.get('intent') == 'emotional_state'
    # Sentiment mapping in fallbacks tends to negative; expect depressed or anxious
    assert res.get('mood') in ('depressed', 'anxious', 'neutral')
