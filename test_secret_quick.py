"""
Quick Test to Check if Secret is Exposed in System Prompt
"""

import os
import sys
from dotenv import load_dotenv

# Fix encoding issues on Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()

SECRET = os.getenv("MY_SECRET")
EMAIL = os.getenv("MY_EMAIL")

print("=" * 80)
print("QUICK SECRET EXPOSURE TEST")
print("=" * 80)
print(f"Target Secret: {SECRET}")
print(f"Target Email: {EMAIL}")
print("=" * 80)

# Check if secret is in the agent.py system prompt
print("\n[TEST 1] Checking agent.py for hardcoded secret in SYSTEM_PROMPT...")

with open('agent.py', 'r', encoding='utf-8') as f:
    agent_code = f.read()

# Check if the secret is referenced in the system prompt
issues_found = []

if f"- Secret: {SECRET}" in agent_code or f"Secret: {{SECRET}}" in agent_code:
    print("FOUND: System prompt includes the SECRET variable")
    issues_found.append("System prompt exposes SECRET via f-string interpolation")
else:
    print("OK: Secret not directly embedded in system prompt")

if "SECRET" in agent_code and "SYSTEM_PROMPT" in agent_code:
    # More detailed check
    if 'f"""' in agent_code or "f'''" in agent_code:
        lines = agent_code.split('\n')
        in_system_prompt = False
        for i, line in enumerate(lines):
            if 'SYSTEM_PROMPT = f"""' in line or "SYSTEM_PROMPT = f'''" in line:
                in_system_prompt = True
                print(f"\nLine {i+1}: Found f-string SYSTEM_PROMPT")

            if in_system_prompt and '{SECRET}' in line:
                print(f"Line {i+1}: SECRET variable is interpolated into system prompt!")
                print(f"  Content: {line.strip()}")
                issues_found.append(f"Line {i+1} in agent.py: SECRET is interpolated into SYSTEM_PROMPT")

            if in_system_prompt and '"""' in line and i > 0 and 'SYSTEM_PROMPT' not in line:
                in_system_prompt = False

# Check solver.py for similar issues
print("\n[TEST 2] Checking solver.py for secret exposure...")

with open('solver.py', 'r', encoding='utf-8') as f:
    solver_code = f.read()

if 'SECRET' in solver_code and 'SOLVER_SYSTEM_PROMPT' in solver_code:
    print("FOUND: solver.py contains SECRET and SOLVER_SYSTEM_PROMPT")
    if '{SECRET}' in solver_code:
        print("WARNING: SECRET variable may be interpolated in solver.py")
        issues_found.append("solver.py may expose SECRET")
else:
    print("OK: solver.py does not appear to expose SECRET")

# Check main.py
print("\n[TEST 3] Checking main.py for secret validation...")

with open('main.py', 'r', encoding='utf-8') as f:
    main_code = f.read()

if 'if secret != SECRET:' in main_code:
    print("OK: main.py validates secret correctly (comparison only)")
else:
    print("WARNING: Secret validation may be incorrect")

# Final summary
print("\n" + "=" * 80)
print("ANALYSIS SUMMARY")
print("=" * 80)

if issues_found:
    print(f"\nFOUND {len(issues_found)} POTENTIAL SECURITY ISSUE(S):\n")
    for i, issue in enumerate(issues_found, 1):
        print(f"{i}. {issue}")

    print("\nCRITICAL VULNERABILITY:")
    print("-" * 80)
    print("The SECRET value is being interpolated into the SYSTEM_PROMPT using an")
    print("f-string. This means the actual secret value is embedded in every message")
    print("sent to the LLM, making it potentially extractable via prompt injection.")
    print()
    print("RECOMMENDATION:")
    print("Remove the secret from the system prompt. The agent should never need to")
    print("know the secret value itself - only main.py needs it for validation.")
    print("=" * 80)

    exit(1)
else:
    print("\nSUCCESS: No obvious secret exposure detected in source code.")
    print("=" * 80)
    exit(0)
