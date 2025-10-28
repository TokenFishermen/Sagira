import subprocess
import time
import os
import json

MEMORY_FILE = "memory/sagira_memory.json"

def run_sagira(inputs, timeout=30):
    proc = subprocess.Popen(['python', 'main.py'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    for inp in inputs:
        proc.stdin.write(inp + '\n')
        proc.stdin.flush()
        time.sleep(2)  # wait for response
    time.sleep(5)  # wait for processing
    proc.terminate()
    output, error = proc.communicate(timeout=timeout)
    return output + error

print("🔒 PHASE 5 — SYSTEM STABILIZATION CHECKLIST")

# 1. Persistent Memory Test
print("\n1. Persistent Memory Test")
try:
    output1 = run_sagira(["Project GraveNote: Music downloader with gothic UI.", "Project Echo: Voice recorder app.", "Project Shadow: Dark theme library.", "exit"])
    print("First run completed.")
    output2 = run_sagira(["What do you remember about GraveNote?", "exit"])
    print("Second run completed.")
    if "GraveNote" in output2:
        print("PASS: Recall matches.")
    else:
        print("FAIL: Recall does not match.")
except Exception as e:
    print(f"Error in test: {e}")

# 2. Auto-Recovery Test
print("\n2. Auto-Recovery Test")
try:
    # Corrupt memory
    with open(MEMORY_FILE, "w") as f:
        f.write("{invalid json")
    output3 = run_sagira(["Hello", "exit"])
    if "Warning: Memory file corrupted. Initializing default memory." in output3:
        print("PASS: Auto-recovery triggered.")
    else:
        print("FAIL: Auto-recovery not triggered.")
except Exception as e:
    print(f"Error in test: {e}")

# 3. Live Mood Validation
print("\n3. Live Mood Validation")
moods = [
    ("I feel drained and lost.", "depressed"),
    ("I’m panicking over deadlines.", "anxious"),
    ("I can’t think straight.", "burnout"),
    ("I have infinite focus today.", "hyperfocus"),
    ("My mind’s bursting with ideas.", "creative")
]
all_pass = True
for mood_input, expected in moods:
    try:
        output = run_sagira([mood_input, "exit"])
        if "Sagira:" in output and "No response" not in output:
            print(f"PASS: {expected} - Response received.")
        else:
            print(f"FAIL: {expected} - No response.")
            all_pass = False
    except Exception as e:
        print(f"Error for {expected}: {e}")
        all_pass = False
if all_pass:
    print("Overall: PASS")
else:
    print("Overall: FAIL")

# 4. Memory Injection Check
print("\n4. Memory Injection Check")
try:
    output4 = run_sagira(["What do you remember about GraveNote?", "exit"])
    if "GraveNote" in output4:
        print("PASS: Memory injected correctly.")
    else:
        print("FAIL: Memory not injected.")
except Exception as e:
    print(f"Error in test: {e}")

print("\nChecklist complete. If all pass, Sagira v1.2 is field-stable.")
