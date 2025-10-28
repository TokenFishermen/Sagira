"""
Example usage of the EntityAwarenessPipeline. This example uses fallback behavior if heavy models are not installed.
"""
from src.entity_awareness import EntityAwarenessPipeline
from src.prompting import build_prompt
from src.memory import InMemoryConversationMemory, KBIndex

# Simple test

def main():
    mem = InMemoryConversationMemory(embedder=None)
    pipeline = EntityAwarenessPipeline(memory=mem)

    conv_history = [
        {"text": "I bought a camera last week."},
        {"text": "The lens arrived damaged."},
    ]

    for text in ["Who are you?", "I am feeling anxious.", "Can you help me return it?"]:
        enriched = pipeline.analyze(text, conversation_history=conv_history, intent_labels=["identity", "emotional_state", "help_request"])
        prompt = build_prompt(enriched, persona={"name":"Sagira","tone":"calm, precise","backstory":"a gothic, loyal assistant"})
        print('---')
        print('User:', text)
        print('Enriched:', enriched)
        print('\nPrompt:\n', prompt[:800])

if __name__ == '__main__':
    main()
