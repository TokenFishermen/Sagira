"""
Prompt builder and persona helpers for entity awareness pipeline.
"""
from typing import Dict, Any, List

DEFAULT_PERSONA = {
    "name": "Ava",
    "tone": "warm, curious, concise",
    "backstory": "friendly assistant that cares about user context and is honest about uncertainty",
}

HUMAN_STYLE_GUIDELINES = """
- Use natural, empathetic language.
- Use contractions when appropriate.
- Show concise reasoning when helpful, but avoid excessive verbosity.
- If unsure, say 'I might be mistaken, but...' and ask a clarifying question.
"""


def _format_entities(entities: List[Dict[str, Any]]) -> str:
    if not entities:
        return "No named entities detected."
    lines = []
    for e in entities:
        lines.append(f"- {e['text']} ({e['label']})")
    return "\n".join(lines)


def build_prompt(enriched: Dict[str, Any], persona: Dict[str, str] = None, style: str = None, max_memory_chars: int = 800) -> str:
    persona = persona or DEFAULT_PERSONA
    style = style or HUMAN_STYLE_GUIDELINES

    memory_blocks = []
    for m in enriched.get("memory_relevant", []):
        txt = m["item"]["text"]
        memory_blocks.append(f"- ({m['score']:.2f}) {txt}")
    memory_text = "\n".join(memory_blocks) or "No relevant memory."

    entities_text = _format_entities(enriched.get("entities", []))
    kb_text = ""
    if enriched.get("kb_matches"):
        kb_lines = []
        for match in enriched["kb_matches"]:
            kb_lines.append(f"Entity: {match['entity']}")
            for m in match["matches"]:
                kb_lines.append(f"  - {m['item']['title']}: {m['item']['text'][:200]} (score={m['score']:.2f})")
        kb_text = "\n".join(kb_lines)

    prompt = f"""
System instructions:
You are {persona['name']}, {persona['backstory']}. Tone: {persona['tone']}.
Follow these style guidelines:
{style}

Context memory (most relevant):
{memory_text}

Detected entities:
{entities_text}

KB matches:
{kb_text}

User message (after coreference resolution):
"""{enriched['resolved_text']}"""

Additional info:
- Sentiment: {enriched['sentiment']}
- If the user expresses an intent, be directive and ask follow-ups to confirm.
- Prefer short clarifying questions if needed.
- Make the response feel human: acknowledge feelings, offer options, use light humor sparingly.
"""
    if len(prompt) > max_memory_chars:
        prompt = prompt[:max_memory_chars] + "\n... (truncated)"
    return prompt.strip()
