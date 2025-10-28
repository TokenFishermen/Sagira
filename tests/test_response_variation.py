import pytest
from core.response_variation import pick_template, list_available_intents, _light_transform
from unittest.mock import patch, mock_open
import random

# Sample test templates
TEST_TEMPLATES = {
    "greeting": ["hello there", "hi friend", "greetings"],
    "farewell": ["goodbye", "see you later"]
}

@pytest.fixture
def mock_templates():
    with patch("core.response_variation.RESPONSE_TEMPLATES", TEST_TEMPLATES):
        yield

def test_pick_template_basic(mock_templates):
    """Test basic template selection works"""
    result = pick_template("greeting", seed=42)
    assert isinstance(result, str)
    assert result.strip().lower() in ["hello there", "hi friend", "greetings"] or \
           any(result.strip().lower().endswith(t) for t in ["hello there", "hi friend", "greetings"])

def test_pick_template_deterministic(mock_templates):
    """Test that seeding produces deterministic results"""
    result1 = pick_template("greeting", seed=123)
    result2 = pick_template("greeting", seed=123)
    assert result1 == result2

def test_pick_template_missing_intent(mock_templates):
    """Test fallback behavior for missing intents"""
    result = pick_template("nonexistent")
    assert "[No template for intent 'nonexistent']" == result

def test_list_available_intents(mock_templates):
    """Test listing available intents"""
    intents = list_available_intents()
    assert set(intents) == {"greeting", "farewell"}

def test_light_transform():
    """Test the transformation function"""
    rnd = random.Random(42)  # Fixed seed for deterministic test
    template = "hello world"
    transformed = _light_transform(template, rnd)
    assert isinstance(transformed, str)
    assert len(transformed) >= len(template)  # Should be at least as long as input

def test_transformations_safe():
    """Test that transformations don't break on edge cases"""
    rnd = random.Random(42)
    edge_cases = ["", "A", "123", "Hi!", "..."]
    for case in edge_cases:
        result = _light_transform(case, rnd)
        assert isinstance(result, str)  # Should always return a string
        assert len(result) >= len(case)  # Should never truncate
