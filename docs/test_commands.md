````markdown
# Runtime Verification Plan for main.py — v0.3.1

This document provides a step-by-step CLI test script for thorough testing of `main.py`. Each step includes the command to run, expected output/behavior, and verification criteria. Run these in sequence in a terminal with the virtual environment activated (e.g., `source .venv/Scripts/activate` on Windows).

## Prerequisites

- Ensure `main.py` is in the current directory (`e:/Sagira`).
- Required dependencies installed (e.g., `llama_cpp`, `colorama`).
- Memory file `memory/sagira_memory.json` exists and is valid JSON.
- Persona files (`persona/sagira_persona.json`, `persona/sagira_prompts.json`) exist.
- Model file `Models/mistral-7b-instruct-v0.2.Q4_K_M.gguf` exists (or adjust path if needed).

## 1. Launch Test

**Command:**

```
python main.py
```

**Expected Behavior:**

- CLI starts and displays: `[INFO] Loading Mistral model... This may take a moment.`
- Followed by: `[INFO] Model loaded successfully.` (if model loads; may take time).
- Then: `Sagira: I am here. What do you need?`
- No import errors, runtime errors, or crashes.

**Verification:**

- If model loading fails (e.g., file not found), note the error. Otherwise, proceed.
- CLI prompt appears without traceback.

## 2. Input Handling Test

**Commands (enter sequentially after launch):**

```
Hello Sagira.
```

```
I'm feeling anxious today.
```

```
Who are you?
```

**Expected Behavior:**

- For each input:
  - Response generated (e.g., starts with `…`).
  - No crashes, empty outputs, or errors.
  - Mood detection: "Hello Sagira." → neutral; "I'm feeling anxious today." → anxious; "Who are you?" → identity intent.

**Verification:**

- Responses appear in format: `Sagira: [colored response]`
- No Python exceptions or hangs.

## 3. Response Logic Test

**Commands (continue from above or restart if needed):**

```
Who are you?
```

```
I feel lost.
```

**Expected Behavior:**

- "Who are you?" → Identity response (e.g., `…I am Sagira — your reflection in the static...`)
- "I feel lost." → Mood template (e.g., anxious or depressed template like `…do one thing, even if small...`)

**Verification:**

- Responses match intent/mood logic from code (check TEMPLATE_POOL and PERSONA).

## 4. Memory System Check

**Commands (after inputs above):**

- Type `exit` to shutdown.
- Then: `python -c "import json; print(json.load(open('memory/sagira_memory.json'))['conversation_history'][-3:])"`

**Expected Behavior:**

- Memory loads on startup (no errors in step 1).
- After inputs, new entries appended to `conversation_history` (e.g., dicts with 'ts', 'role', 'text', 'mood', 'mode').

**Verification:**

- JSON output shows recent entries matching inputs (e.g., user inputs and Sagira responses).

## 5. Graceful Exit Test

**Command (during running CLI):**

```
exit
```

**Expected Behavior:**

- Displays: `Sagira: Until next time.`
- Clean shutdown, no traceback.

**Verification:**

- Terminal returns to prompt without errors.

## 6. Log Inspection

**Command (after shutdown):**

```
python -c "import os; logs = [f for f in os.listdir('.') if 'conditioning' in f and 'logs' in f]; print('Logs found:', logs); [print(open(f).read()[-500:]) for f in logs if os.path.exists(f)]"
```

**Expected Behavior:**

- Logs like `conditioning_test_logs.txt` or similar updated with timestamps and response entries.

**Verification:**

- Recent entries include test inputs/responses with dates.

## Summary

- If all steps pass without errors, mark **v0.3.1 Verified**.
- If any fail, capture full error trace and last Sagira output for analysis.
- Run in a clean terminal session for each test cycle.
````
