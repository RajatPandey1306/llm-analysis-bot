import asyncio
import logging
import sys
from solver import execute_code

# Redirect stdout/stderr to file
sys.stdout = open('test_encoding_output.txt', 'w', encoding='utf-8')
sys.stderr = sys.stdout

logging.basicConfig(level=logging.INFO, stream=sys.stdout)

async def test():
    print("Testing Encoding Fix...")
    # Code with non-ascii character
    code = """
print("Hello World \u2011")
"""
    try:
        result = await execute_code(code)
        print(f"\nResult: {result}")
    except Exception as e:
        print(f"\nError: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(test())
    except Exception as e:
        print(f"Fatal error: {e}")
    finally:
        sys.stdout.close()
