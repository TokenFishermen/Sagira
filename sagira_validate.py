# sagira_validate.py
import json, os, time
from main import detect_mood, generate_response, TEMPLATE_POOL, save_memory, load_memory

LOG_FILE = "logs/validation.log"
os.makedirs("logs", exist_ok=True)

mood_samples = {
    "anxious": ["I'm really overwhelmed", "I can’t stop worrying", "I feel tense today"],
    "depressed": ["Nothing feels worth it", "I'm tired of everything", "I just feel numb"],
    "hyperfocus": ["I can’t stop coding", "I’ve been locked in for hours", "I'm laser focused"],
    "creative": ["I have this wild idea", "Let’s try something artistic", "My head’s full of colors"],
    "burnout": ["I can’t keep going", "I'm exhausted", "I just want to stop"]
}

modes = ["GROUNDING", "EXECUTION", "CREATIVE", "MAINTENANCE", "ARCHIVE"]

def log(msg):
    with open(LOG_FILE, "a") as f:
        f.write(f"{time.strftime('%H:%M:%S')} | {msg}\n")
    print(msg)

def validate_mood_detection():
    log("\n--- Mood Detection ---")
    for mood, phrases in mood_samples.items():
        passed = 0
        for text in phrases:
            detected = detect_mood(text)
            if detected == mood:
                passed += 1
        log(f"{mood.upper()}: {passed}/{len(phrases)} correct")

def validate_response_templates():
    log("\n--- Template Presence ---")
    for mood in mood_samples.keys():
        if mood in TEMPLATE_POOL and TEMPLATE_POOL[mood]:
            log(f"{mood.upper()}: OK ({len(TEMPLATE_POOL[mood])} templates)")
        else:
            log(f"{mood.upper()}: MISSING TEMPLATES")

def validate_fallback_logic():
    log("\n--- Fallback Check ---")
    missing = [m for m in mood_samples if m not in TEMPLATE_POOL or not TEMPLATE_POOL[m]]
    for mood in missing:
        text = mood_samples[mood][0]
        try:
            response = generate_response(text)
            if response:
                log(f"{mood.upper()}: Fallback working")
            else:
                log(f"{mood.upper()}: Fallback FAILED")
        except Exception as e:
            log(f"{mood.upper()}: ERROR {e}")

def validate_memory_cycle():
    log("\n--- Memory Persistence ---")
    memory = {"test": "persistence_check"}
    save_memory(memory)
    reloaded = load_memory()
    if reloaded.get("test") == "persistence_check":
        log("Memory: PASS")
    else:
        log("Memory: FAIL")

def main():
    log("=== SAGIRA VALIDATION SUITE v1.0 START ===")
    validate_mood_detection()
    validate_response_templates()
    validate_fallback_logic()
    validate_memory_cycle()
    log("=== VALIDATION COMPLETE ===")

if __name__ == "__main__":
    main()
