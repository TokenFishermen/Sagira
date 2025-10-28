import os
import json
import time
import re
import random
import sys
import argparse
from llama_cpp import Llama
from colorama import init, Fore, Back, Style
from core import nlp_core

# Initialize colorama for colored CLI output
init(autoreset=True)

# Parse arguments
parser = argparse.ArgumentParser()
parser.add_argument('--debug', action='store_true', help='Enable debug mode')
parser.add_argument('--use-ea', action='store_true', help='Use Entity Awareness enrichment pipeline')
args = parser.parse_args()

# Paths
MODEL_PATH = "Models/mistral-7b-instruct-v0.2.Q4_K_M.gguf"
MEMORY_FILE = "memory/sagira_memory.json"
PERSONA_FILE = "persona/sagira_persona.json"
PROMPTS_FILE = "persona/sagira_prompts.json"

# Ensure directories exist
os.makedirs("memory", exist_ok=True)
os.makedirs("persona", exist_ok=True)

# Load or initialize memory
if os.path.exists(MEMORY_FILE):
    try:
        with open(MEMORY_FILE, "r") as f:
            memory = json.load(f)
    except json.JSONDecodeError:
        print("Warning: Memory file corrupted. Initializing default memory.")
        memory = {
            "user_profile": {
                "name": "User",
                "preferred_alias": "User",
                "timezone": "UTC",
                "work_rhythm": "flexible",
                "preferred_palette_format": ".gpl",
                "safety_flags": ["anxiety", "depression", "ADHD"]
            },
            "projects": {},
            "user_state": {
                "energy": 5,
                "mood": "neutral",
                "focus_minutes": 30,
                "last_break": time.time()
            },
            "rituals": {
                "start_work": ["make tea", "open VSCode workspace", "start 25m timer"]
            },
            "conversation_history": []
        }
else:
    memory = {
        "user_profile": {
            "name": "User",
            "preferred_alias": "User",
            "timezone": "UTC",
            "work_rhythm": "flexible",
            "preferred_palette_format": ".gpl",
            "safety_flags": ["anxiety", "depression", "ADHD"]
        },
        "projects": {},
        "user_state": {
            "energy": 5,
            "mood": "neutral",
            "focus_minutes": 30,
            "last_break": time.time()
        },
        "rituals": {
            "start_work": ["make tea", "open VSCode workspace", "start 25m timer"]
        },
        "conversation_history": []
    }

# === Load Persona & Prompts ===
def load_persona():
    try:
        with open(PERSONA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print("Persona file not found. Initializing default persona...")
        return {
            "name": "Sagira",
            "archetype": "Shadow Guide",
            "modes": ["GROUNDING", "EXECUTION", "CREATIVE", "MAINTENANCE", "ARCHIVE"],
            "voice": {
                "tone": "calm, precise, slightly poetic",
                "sentence_length": "short-medium",
                "ellipsis_usage": True,
                "exclamation_forbidden": True
            }
        }
    except json.JSONDecodeError:
        print("Persona file corrupted. Loading default persona...")
        return {
            "name": "Sagira",
            "archetype": "Shadow Guide",
            "modes": ["GROUNDING", "EXECUTION", "CREATIVE", "MAINTENANCE", "ARCHIVE"],
            "voice": {
                "tone": "calm, precise, slightly poetic",
                "sentence_length": "short-medium",
                "ellipsis_usage": True,
                "exclamation_forbidden": True
            }
        }

def load_prompts():
    try:
        with open(PROMPTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        print("Prompts file not found or corrupted. Loading default prompts...")
        return {
            "system": "You are Sagira, a calm and precise AI guide...",
            "modes": {
                "GROUNDING": "Grounding mode: Provide calm, centering guidance...",
                "EXECUTION": "Execution mode: Assist with tasks step by step...",
                "CREATIVE": "Creative mode: Encourage exploration and ideas...",
                "MAINTENANCE": "Maintenance mode: Help with rest and recovery...",
                "ARCHIVE": "Archive mode: Organize and remember information..."
            }
        }

PERSONA = load_persona()
PROMPTS = load_prompts()

# === Core Persona Parameters ===
SAGIRA_NAME = PERSONA.get("name", "Sagira")
SAGIRA_ARCHETYPE = PERSONA.get("archetype", "Guide")
VOICE_SETTINGS = PERSONA.get("voice", {})
MODES = PERSONA.get("modes", [])

def get_mode_prompt(mode):
    key = mode.upper()
    return PROMPTS.get("modes", {}).get(key, "")

def derive_mood_from_analysis(analysis):
    intent = analysis["intent_guess"]
    sentiment = analysis["sentiment"]
    keywords = analysis["keywords"]

    # Mapping based on intent and sentiment
    if intent == "emotional_state":
        if sentiment < -0.2:
            return "depressed"
        elif sentiment > 0.2:
            return "creative"
        else:
            return "neutral"
    elif intent == "productivity":
        if sentiment < 0:
            return "anxious"
        else:
            return "neutral"
    elif intent == "identity_query":
        return "neutral"
    elif intent == "purpose_query":
        return "neutral"
    else:
        # Fallback to keywords
        if any(k in ["tired", "exhausted", "drained"] for k in keywords):
            return "depressed"
        elif any(k in ["creative", "inspired", "idea"] for k in keywords):
            return "creative"
        elif any(k in ["worried", "anxious", "stuck"] for k in keywords):
            return "anxious"
        else:
            return "neutral"

# Function to get mode based on mood and user_state
def get_mode(mood, user_state):
    energy = user_state.get("energy", 5)
    if mood == "anxious" or mood == "depressed" or energy < 5:
        return "GROUNDING"
    elif mood == "creative":
        return "CREATIVE"
    elif mood == "hyperfocus":
        return "MAINTENANCE"
    elif mood == "burnout":
        return "MAINTENANCE"
    else:
        return "EXECUTION"

# Function to polish response
def polish_response(response, mood=None):
    if not response.startswith("…"):
        response = "…" + response
    response = response.replace("!", "")  # Remove any accidental exclamations
    # Optionally split long sentences
    if len(response.split()) > 20:
        response = " ".join(response.split()[:18]) + "…"

    # Add hesitation markers based on mood
    if mood == "anxious":
        response = response.replace(".", "…").replace(",", "…")
    elif mood == "depressed":
        response = response.lower().replace(".", "…")
    elif mood == "creative":
        response = response + "…"

    # Dynamic sentence rhythm: short when grounding, longer when reflecting
    if mood in ["anxious", "depressed"]:
        sentences = response.split(".")
        if len(sentences) > 1:
            response = ". ".join(sentences[:1]) + "."
    elif mood == "creative":
        # Allow longer for reflection
        pass

    return response

# TEMPLATE_POOL for dynamic response variation
TEMPLATE_POOL = {
    "neutral": [
        "…consider your next step carefully.",
        "Focus on the task at hand, then move forward.",
        "…organize your workspace before you proceed."
    ],
    "anxious": [
        "Take a deep breath… slow it down.",
        "…center yourself with one small, clear task.",
        "Focus on your hands; let the mind settle."
    ],
    "depressed": [
        "…do one thing, even if small, to move forward.",
        "Break the cycle: a single task will guide you.",
        "…focus on completion rather than perfection."
    ],
    "creative": [
        "…explore the shadow of the idea, twist it.",
        "What if you combine the unexpected… and practical?",
        "…let the imagery flow, but note the core structure."
    ],
    "hyperfocus": [
        "…pause, drink water, stretch your shoulders.",
        "Check your posture and eyes; reset briefly.",
        "…log the progress; brief rest restores clarity."
    ],
    "burnout": [
        "…rest is the next step, not pressure.",
        "Step away, even briefly, before continuing.",
        "…let the body recover before the mind resumes."
    ]
}

# Function to save memory
def save_memory(mem):
    with open(MEMORY_FILE, "w") as f:
        json.dump(mem, f, indent=4)

# Function to load memory
def load_memory():
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            print("Warning: Memory file corrupted.")
            return {}
    return {}

def apply_personality_filter(text, mood=None):
    tone = VOICE_SETTINGS.get("tone", "calm")
    ellipsis = "…" if VOICE_SETTINGS.get("ellipsis_usage") else ""
    short = VOICE_SETTINGS.get("sentence_length", "short") == "short"

    # Adjust based on mood
    if mood == "depressed":
        text = text.lower().replace(".", "…")
    elif mood == "hyperfocus":
        text = text.replace(" ", "")
    elif mood == "creative":
        text = text + ellipsis
    elif mood == "burnout":
        text = text.strip() + " …pause."
    elif mood == "anxious":
        text = text.replace(".", "…").replace(",", "…")

    # Tone enforcement
    text = text.replace("!", "")  # forbid exclamation marks
    if short:
        sentences = text.split(".")
        text = ". ".join(s.strip() for s in sentences[:2])

    # Add calm coloration
    return f"{Fore.WHITE}{text}{Style.RESET_ALL}"

def humanize_response(text):
    text = text.strip()
    if not text.startswith("…"):
        text = "…" + text[0].lower() + text[1:]
    text = text.replace(" .", ".").replace(" ,", ",")
    return text

# Function to search memory for relevant context
def memory_search(user_input, tags=None):
    relevant = []
    input_lower = user_input.lower()
    for category in ["projects", "rituals", "knowledge"]:
        if category in memory:
            for key, item in memory[category].items():
                if isinstance(item, dict):
                    # Check key, description or other fields
                    key_lower = key.lower()
                    desc = item.get("description", "").lower()
                    if any(word in input_lower.split() for word in [key_lower] + desc.split()) or (tags and any(tag in item.get("tags", []) for tag in tags)):
                        relevant.append((category, key, item))
                    # Also check nested keys for knowledge
                    if category == "knowledge":
                        for subkey, subitem in item.items():
                            if isinstance(subitem, dict):
                                subdesc = subitem.get("description", "").lower()
                                if any(word in input_lower.split() for word in subdesc.split()):
                                    relevant.append((category, subkey, subitem))
    return relevant

# Function to integrate context into template
def integrate_context(template, relevant_memory):
    if not relevant_memory:
        return template
    # Simple integration: append a reference
    category, key, item = relevant_memory[0]  # Take first relevant
    if category == "projects":
        ref = f" Recall your project '{key}': {item.get('next_step_suggestion', 'continue work')}."
    elif category == "rituals":
        ref = f" Consider your ritual '{key}' last performed {item.get('last_performed', 'recently')}."
    elif category == "knowledge":
        ref = f" From knowledge: {item.get('description', 'relevant info')}."
    else:
        ref = ""
    return template + ref

# Function to log interaction in memory
def log_interaction(user_input, response, mood, mode, relevant_memory):
    # Update conversation_history
    memory["conversation_history"].append({
        "date": time.strftime("%Y-%m-%d"),
        "topic": user_input[:50],  # Truncate
        "mood_detected": mood,
        "mode_used": mode,
        "summary": response[:100]
    })
    # Update experience_log
    memory["experience_log"].append({
        "date": time.strftime("%Y-%m-%d"),
        "activity": f"Responded to '{user_input[:30]}...'",
        "mood_detected": mood
    })
    # Update user_state
    memory["user_state"]["current_mood"] = mood
    # Save memory
    save_memory(memory)

# Function to generate response
def generate_response(user_input):
    from emotion_engine import EmotionEngine
    engine = EmotionEngine()
    # Debug input -> emotion engine
    if args.debug:
        print(f"[DEBUG] generate_response input: {user_input}")
    intent_data = engine.detect_intent(user_input)
    intent = intent_data["intent"]
    mood = intent_data["mood"]
    if args.debug:
        print(f"[DEBUG] generate_response detected intent: {intent}, mood: {mood}")

    # Use response variation system for all templates
    from core.response_variation import pick_template

    # Use mood and intent for template selection with deterministic but varying seed
    seed = len(memory.get("conversation_history", [])) # Use conversation length as seed
    response = pick_template(intent, seed=seed)

    # Apply emotional blending
    blended_mood = engine.blend_affective_trace(mood)

    # Retrieve and integrate relevant memory
    relevant_memory = memory_search(user_input)

    # Only use TEMPLATE_POOL as fallback if response variation fails
    if not response and blended_mood in TEMPLATE_POOL:
        base_response = random.choice(TEMPLATE_POOL[blended_mood])
        # Integrate context
        base_response = integrate_context(base_response, relevant_memory)
        final_response = polish_response(base_response, blended_mood)
        return final_response
    else:
        # Fallback to LLM generation (simplified)
        base_response = f"LLM response for {blended_mood} mode"
        final_response = polish_response(base_response, blended_mood)
        return final_response

# Function for graceful exit
def graceful_exit():
    print(Fore.MAGENTA + "Sagira: " + Fore.WHITE + "Until next time.")
    # Save memory before exit
    save_memory(memory)
    sys.exit(0)

if __name__ == "__main__":
    # Load the model
    print(Fore.CYAN + "Loading Mistral model... This may take a moment.")
    try:
        llm = Llama(model_path=MODEL_PATH, n_ctx=2048, n_threads=4)
        print(Fore.GREEN + "Model loaded successfully.")
    except Exception as e:
        print(Fore.RED + f"Error loading model: {e}")
        sys.exit(1)

    # CLI chat loop
    print(Fore.MAGENTA + "Sagira: " + Fore.WHITE + "I am here. What do you need?")
    while True:
        user_input = input(Fore.BLUE + "You: " + Style.RESET_ALL).strip()
        if user_input.lower() in ["exit", "quit"]:
            graceful_exit()

        # Update memory with user input
        memory["conversation_history"].append({"ts": time.time(), "role": "user", "text": user_input, "mood": "", "mode": ""})

        # Detect mood and get mode
        # Optionally use the Entity Awareness adapter
        if args.use_ea:
            try:
                from core.ea_adapter import EAAdapter
                engine = EAAdapter()
            except Exception:
                from emotion_engine import EmotionEngine
                engine = EmotionEngine()
        else:
            from emotion_engine import EmotionEngine
            engine = EmotionEngine()

        if args.debug:
            print(f"[DEBUG] Input received: {user_input}")
        intent_data = engine.detect_intent(user_input)
        intent = intent_data["intent"]
        mood = intent_data["mood"]
        if args.debug:
            print(f"[DEBUG] Detected intent: {intent}, mood: {mood}")
        mode = get_mode(mood, memory["user_state"])

        # Update last entry with mood and mode
        memory["conversation_history"][-1]["mood"] = mood
        memory["conversation_history"][-1]["mode"] = mode

        # Build prompt
        system_prompt = PROMPTS["system"]
        mode_guidance = get_mode_prompt(mode)
        relevant_memory = memory_search(user_input)
        context_snippet = ""
        if relevant_memory:
            category, key, item = relevant_memory[0]
            if category == "projects":
                context_snippet = f" Recall your project '{key}': {item.get('next_step_suggestion', 'continue work')}."
            elif category == "rituals":
                context_snippet = f" Consider your ritual '{key}' last performed {item.get('last_performed', 'recently')}."
            elif category == "knowledge":
                context_snippet = f" From knowledge: {item.get('description', 'relevant info')}."
        persona_context = "Sagira is calm, loyal, gothic, analytical, and humanlike in speech.\n"
        full_prompt = persona_context + f"{system_prompt}\n\n[Current Mode: {mode}]\n{mode_guidance}\n\nConversation history: {json.dumps(memory['conversation_history'][-5:])}\n{context_snippet}\nUser: {user_input}\nSagira:"

        # Generate response
        try:
            output = llm(full_prompt, max_tokens=300, temperature=0.5, stop=["User:", "\n"])
            response = output["choices"][0]["text"].strip()
        except Exception as e:
            response = f"Error generating response: {e}"

        # Use TEMPLATE_POOL for variation if available
        if mood in TEMPLATE_POOL:
            response = random.choice(TEMPLATE_POOL[mood])
            if args.debug:
                print(f"[DEBUG] Template found for mood '{mood}': {response}")
        else:
            if args.debug:
                print(f"[DEBUG] No template found for mood '{mood}'. Using LLM response: {response}")

        # Apply personality filter and humanize
        response = apply_personality_filter(response, mood)
        response = humanize_response(response)

        # Add affective trace to memory
        affective_trace = {
            "mood": mood,
            "tone": "steady" if mood == "neutral" else ("tense" if mood == "anxious" else ("somber" if mood == "depressed" else ("inspired" if mood == "creative" else "calm"))),
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(time.time()))
        }
        memory["conversation_history"][-1]["affective_trace"] = affective_trace

        # Print mode
        # print(f"{Fore.CYAN}[MODE: {mode}] {Style.RESET_ALL}")
        # print(get_mode_prompt(mode))

        # Color response (gothic theme: midnight blue background, bone white text)
        colored_response = Back.BLUE + Fore.WHITE + response + Style.RESET_ALL

        print(Fore.MAGENTA + "Sagira: " + colored_response)

        # Update memory with response
        memory["conversation_history"].append({"ts": time.time(), "role": "sagira", "text": response, "mood": mood, "mode": mode})

        # Save memory
        with open(MEMORY_FILE, "w") as f:
            json.dump(memory, f, indent=4)
