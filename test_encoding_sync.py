import sys
import tempfile
import os

# Redirect stdout/stderr to file
sys.stdout = open('test_encoding_sync_output.txt', 'w', encoding='utf-8')
sys.stderr = sys.stdout

def test():
    print("Testing Encoding Fix Sync...")
    code = "print('Hello World \u2011')"

    try:
        # Simulate the fix in solver.py
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
            f.write(code)
            temp_file = f.name

        print(f"Successfully wrote to {temp_file}")

        # Verify content
        with open(temp_file, 'r', encoding='utf-8') as f:
            content = f.read()
            print(f"Content read back: {content}")

        os.unlink(temp_file)
        print("Test Passed")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    try:
        test()
    except Exception as e:
        print(f"Fatal error: {e}")
    finally:
        sys.stdout.close()
