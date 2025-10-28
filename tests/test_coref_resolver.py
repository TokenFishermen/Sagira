import pytest
from core.coref_resolver import simple_coref_resolver, get_conversation_entities

def test_basic_pronoun_resolution():
    conv = [
        {"text": "I bought a camera last week."},
        {"text": "The lens arrived damaged."}
    ]
    text = "Can you help me return it?"
    resolved = simple_coref_resolver(text, conv)
    assert "lens" in resolved.lower(), "Should resolve 'it' to 'lens'"

def test_gender_specific_resolution():
    conv = [
        {"text": "John is a good programmer."},
        {"text": "Sarah is an excellent designer."}
    ]

    # Test male pronoun
    text1 = "He writes clean code."
    resolved1 = simple_coref_resolver(text1, conv)
    assert "john" in resolved1.lower(), "Should resolve 'he' to 'John'"

    # Test female pronoun
    text2 = "She creates beautiful interfaces."
    resolved2 = simple_coref_resolver(text2, conv)
    assert "sarah" in resolved2.lower(), "Should resolve 'she' to 'Sarah'"

def test_plural_resolution():
    conv = [{"text": "The developers fixed several bugs."}]
    text = "They worked hard on it."
    resolved = simple_coref_resolver(text, conv)
    assert "developers" in resolved.lower(), "Should resolve 'they' to 'developers'"

def test_fallback_behavior():
    """Test that resolver doesn't crash with empty/invalid input"""
    # Empty conversation
    assert simple_coref_resolver("It works", []) == "It works"
    # No conversation history
    assert simple_coref_resolver("It works", None) == "It works"
    # Empty text
    assert simple_coref_resolver("", [{"text": "something"}]) == ""

def test_entity_extraction():
    conv = [
        {"text": "The camera has a broken lens."},
        {"text": "Microsoft released a new update."},
        {"text": "John's laptop needs repair."}
    ]
    entities = get_conversation_entities(conv)
    assert "camera" in entities
    assert "Microsoft" in entities
    assert "John" in entities
    assert "laptop" in entities
