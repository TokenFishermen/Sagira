from src.coref_resolver import simple_coref_resolver

def test_coref_resolves_it_to_recent_noun():
    history = [
        {"text": "I bought a camera last week."},
        {"text": "The lens arrived damaged."}
    ]
    text = "Can you help me return it?"
    out = simple_coref_resolver(text, history)
    assert 'lens' in out.lower() or 'camera' in out.lower()

def test_coref_no_history_returns_original():
    text = "Return it please"
    out = simple_coref_resolver(text, [])
    assert out == text
