import json

def test_persona_templates_exist_and_have_variants():
    path = 'persona/response_templates.json'
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    # required intents
    required = ['identity_query', 'emotional_state', 'assistance', 'productivity', 'general_chat']
    for r in required:
        assert r in data
        assert isinstance(data[r], list)
        assert len(data[r]) >= 4
