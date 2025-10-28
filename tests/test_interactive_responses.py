#!/usr/bin/env python
"""Interactive test harness for Sagira's response variation system."""

import sys
import random
from pathlib import Path
from typing import Dict, Any

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from emotion_engine import EmotionEngine
from core.response_variation import pick_template

def main():
    print("=== Sagira Interactive Response Test ===")
    print("Commands:")
    print("  'quit' or 'exit' to end")
    print("  'seed N' to set deterministic seed")
    print("  'intents' to list available intents")
    print("\n")

    engine = EmotionEngine()
    conversation_count = 0
    current_seed = None

    while True:
        try:
            user_input = input("You: ").strip()
            if user_input.lower() in ["quit", "exit"]:
                break

            # Special commands
            if user_input.lower().startswith("seed "):
                try:
                    current_seed = int(user_input.split()[1])
                    print(f"Set deterministic seed to {current_seed}")
                    continue
                except (IndexError, ValueError):
                    print("Invalid seed value. Use 'seed N' where N is an integer.")
                    continue

            if user_input.lower() == "intents":
                from core.response_variation import list_available_intents
                intents = list_available_intents()
                print("\nAvailable intents:")
                for intent in sorted(intents):
                    print(f"  - {intent}")
                print()
                continue

            # Process input through emotion engine
            intent_data = engine.detect_intent(user_input)
            intent = intent_data["intent"]
            mood = intent_data["mood"]

            # Use conversation count or explicit seed
            seed = current_seed if current_seed is not None else conversation_count

            # Get response with variation
            response = pick_template(intent, seed=seed)

            # Print debug info and response
            print(f"\nDebug:")
            print(f"  Intent: {intent}")
            print(f"  Mood: {mood}")
            print(f"  Seed: {seed}")
            print(f"\nSagira: {response}\n")

            conversation_count += 1

        except KeyboardInterrupt:
            print("\nGracefully exiting...")
            break
        except Exception as e:
            print(f"Error: {e}")
            continue

if __name__ == "__main__":
    main()
