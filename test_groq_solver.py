import asyncio
import logging
import sys
from solver import solve_with_llm

# Redirect stdout/stderr to file
sys.stdout = open('test_output.txt', 'w')
sys.stderr = sys.stdout

logging.basicConfig(level=logging.INFO, stream=sys.stdout)

async def test():
    print("Testing Groq Solver...")
    question = "Write a python script to print 'Hello Groq'. Print ONLY the string."
    details = {"raw_html": "<html></html>", "decoded_html": ""}

    try:
        code = await solve_with_llm(question, details)
        print("\nGenerated Code:")
        print(code)
    except Exception as e:
        print(f"\nError: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(test())
    except Exception as e:
        print(f"Fatal error: {e}")
    finally:
        sys.stdout.close()
