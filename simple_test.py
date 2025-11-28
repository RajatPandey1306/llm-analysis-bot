from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

print("Starting simple test...")
try:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY environment variable is not set")
    client = Groq(api_key=api_key)
    print("Client initialized.")
    completion = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[{"role": "user", "content": "Say hi"}],
        max_completion_tokens=10
    )
    print("Response received:")
    print(completion.choices[0].message.content)
except Exception as e:
    print(f"Error: {e}")
print("Test complete.")
