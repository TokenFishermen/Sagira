# core/response_variation.py
import json
import random
from pathlib import Path
from typing import List, Optional

# Load templates
TEMPLATE_FILE = Path(__file__).parent.parent / "persona" / "response_templates.json"

try:
    with open(TEMPLATE_FILE, "r", encoding="utf-8") as f:
        RESPONSE_TEMPLATES = json.load(f)
except FileNotFoundError:
    RESPONSE_TEMPLATES = {}  # fallback to empty dict

def pick_template(intent: str, seed: Optional[int] = None) -> str:
    """
    Pick a template for a given intent with optional deterministic seeding.
    """
    templates: List[str] = RESPONSE_TEMPLATES.get(intent, [])
    if not templates:
        return f"[No template for intent '{intent}']"

    rnd = random.Random(seed)
    template = rnd.choice(templates)
    return _light_transform(template, rnd)

def _light_transform(template: str, rnd: random.Random) -> str:
    """
    Apply minimal, safe transformations to increase variety.
    Currently:
      - Optional insertion of ellipses or pauses
      - Minor capitalization tweaks
      - Optional interjection for casual tone
    """
    # 10% chance to add ellipsis
    if rnd.random() < 0.1:
        template = template + "..."

    # 10% chance to prepend a mild interjection
    interjections = ["Hmm,", "Ah,", "Well,", "Okay,"]
    if rnd.random() < 0.1:
        template = f"{rnd.choice(interjections)} {template}"

    # Randomly capitalize first word (5% chance)
    if rnd.random() < 0.05 and template:
        template = template[0].upper() + template[1:]

    return template

# Optional helper
def list_available_intents() -> List[str]:
    return list(RESPONSE_TEMPLATES.keys())

if __name__ == "__main__":
    # Quick demo
    for intent in list_available_intents():
        print(f"Intent: {intent}")
        for i in range(3):
            print("  →", pick_template(intent, seed=i))
