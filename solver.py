"""
LLM-powered Solver that generates Python code to solve quiz questions
"""

from groq import Groq
import os
import logging
import json
import re
from typing import Any

logger = logging.getLogger(__name__)

# Initialize Groq client
# Using the provided API key from environment variables
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY environment variable is not set")


SOLVER_SYSTEM_PROMPT = """You are an expert Python data analyst and automation engineer. Your task is to analyze quiz questions and write Python code to solve them.

You will receive:
1. A quiz question (possibly with HTML/markdown formatting)
2. Context about the task (URLs to download data, instructions, etc.)

Your job:
1. Understand what the question is asking
2. Write a complete, self-contained Python script that:
   - Downloads any necessary data files
   - Processes the data (CSV, PDF, Excel, images, etc.)
   - Performs the required analysis (filtering, aggregation, calculations, visualization)
   - Prints ONLY the final answer in the exact format requested

CRITICAL RULES:
- Your code must be complete and executable
- Use standard libraries: requests, pandas, pdfplumber, matplotlib, etc.
- Handle errors gracefully
- Print ONLY the final answer (number, string, JSON, etc.) - no debug output
- IMPORTANT: Do NOT submit the answer to the server in your code. Just print the answer. The calling system will handle the submission.
- If the question asks you to "POST" or "submit" the answer, IGNORE that instruction. Your job is only to find/calculate the answer and print it. The agent will handle the actual POST request.
- When using `requests`, always set a standard 'User-Agent' header to avoid 403 errors.
- If the answer should be an image, save it and print the base64-encoded data URI
- If the answer is a JSON object, print valid JSON
- The code will run in isolation - include all imports and setup
- HANDLING CSV FILES:
  - Check if the CSV has a header. If the first row looks like data (e.g. numbers), use `header=None`.
  - When in doubt, read with `header=None` and inspect the first few rows.
  - If `pd.read_csv` fails with `ParserError`, try reading the file as text first, or use `sep=None` with `engine='python'`, or force `sep=','`.
  - **CRITICAL**: If the question mentions a "Cutoff" value, the task is almost always to **SUM all numbers strictly GREATER than the cutoff**.
    - Logic: `sum(x for x in data if x > cutoff)`.
    - Do NOT calculate the total sum (unless no cutoff).
    - Do NOT count the numbers.
    - Do NOT find the max/min.

- HANDLING JS-RENDERED PAGES:
  - If the page content is empty or only contains `<script>` tags (like `<script src="...">`), the data IS in the script file.
  - **YOU MUST** fetch the `.js` file referenced in `src` (e.g., `demo-scrape.js`).
  - Construct the full URL for the .js file and download it.
  - Look for the secret/data inside the JS code (regex/parsing).

Example 1 (Sum from CSV):
Question: "Download data.csv. What is the sum of the 'value' column?"
Your code:
```python
import requests
import pandas as pd

# Download file
response = requests.get('https://example.com/data.csv')
with open('data.csv', 'wb') as f:
    f.write(response.content)

# Process
df = pd.read_csv('data.csv')
result = df['value'].sum()

# Output ONLY the answer
print(result)
```

Example 2 (PDF extraction):
Question: "Download report.pdf. What is the value in the table on page 2?"
Your code:
```python
import requests
import pdfplumber

# Download
response = requests.get('https://example.com/report.pdf')
with open('report.pdf', 'wb') as f:
    f.write(response.content)

# Extract
with pdfplumber.open('report.pdf') as pdf:
    page = pdf.pages[1]  # Page 2 (0-indexed)
    tables = page.extract_tables()
    # Process tables to find the answer
    result = tables[0][1][1]  # Adjust based on actual structure

print(result)
```

Example 3 (Chart generation):
Question: "Create a bar chart and submit as image"
Your code:
```python
import matplotlib.pyplot as plt
import base64
from io import BytesIO

# Create chart
plt.figure(figsize=(10, 6))
plt.bar(['A', 'B', 'C'], [10, 20, 15])
plt.title('Sample Chart')

# Save to base64
buffer = BytesIO()
plt.savefig(buffer, format='png')
buffer.seek(0)
img_base64 = base64.b64encode(buffer.read()).decode()

print(f"data:image/png;base64,{img_base64}")
```

Now, given the question below, write the complete Python code to solve it."""


async def solve_with_llm(question: str, quiz_details: dict, feedback: str = None) -> str:
    """
    Use LLM to generate Python code that solves the quiz question

    Args:
        question: The quiz question text
        quiz_details: Additional context (HTML, URLs, etc.)
        feedback: Feedback from previous failed attempt (optional)

    Returns:
        Python code as string
    """
    logger.info("Generating solution code with LLM")

    user_prompt = f"""Quiz Question:
{question}

Additional Context:
- Current URL: {quiz_details.get('current_url', 'Unknown')}
- Raw HTML available: {len(quiz_details.get('raw_html', ''))} characters
- Decoded content: {quiz_details.get('decoded_html', '')[:500]}...
"""

    if feedback:
        user_prompt += f"\nPREVIOUS ATTEMPT FAILED. Feedback from server:\n{feedback}\n\nIMPORTANT: Adjust your code to fix the issue described above."

    user_prompt += """
Generate the Python code to solve this question. Remember to:
1. Extract any URLs mentioned in the question
2. Download necessary files
3. Process the data appropriately
4. Print ONLY the final answer in the correct format"""

    try:
        # Initialize Groq client
        client = Groq(api_key=GROQ_API_KEY)

        completion = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {"role": "system", "content": SOLVER_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            temperature=1,
            max_completion_tokens=8192,
            top_p=1,
            reasoning_effort="medium",
            stream=True,
            stop=None
        )

        code = ""
        for chunk in completion:
            code += chunk.choices[0].delta.content or ""

        # Extract code from markdown code blocks if present
        code = extract_code_from_markdown(code)

        logger.info(f"Generated code:\n{code}")

        return code

    except Exception as e:
        logger.error(f"Error calling Groq API: {e}")
        raise


def extract_code_from_markdown(text: str) -> str:
    """Extract Python code from markdown code blocks"""
    # Look for ```python ... ``` blocks
    pattern = r'```(?:python)?\s*\n(.*?)```'
    matches = re.findall(pattern, text, re.DOTALL)

    if matches:
        # Return the first code block found
        return matches[0].strip()
    else:
        # If no code blocks, return the text as-is
        return text.strip()


async def execute_code(code: str, timeout: int = 120) -> Any:
    """
    Execute the generated Python code and capture output

    Args:
        code: Python code to execute
        timeout: Maximum execution time in seconds

    Returns:
        The output/answer from the code
    """
    logger.info("Executing generated code")

    import subprocess
    import tempfile
    import os

    # Create a temporary file for the code
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
        f.write(code)
        temp_file = f.name

    try:
        # Execute the code in a subprocess for isolation
        result = subprocess.run(
            ['python', temp_file],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=os.path.dirname(temp_file)
        )

        # Clean up temp file
        os.unlink(temp_file)

        if result.returncode != 0:
            logger.error(f"Code execution failed: {result.stderr}")
            raise Exception(f"Code execution error: {result.stderr}")

        # Get the output
        output = result.stdout.strip()
        logger.info(f"Code output: {output}")

        # Try to parse as JSON if it looks like JSON
        if output.startswith('{') or output.startswith('['):
            try:
                return json.loads(output)
            except:
                pass

        # Try to parse as number
        try:
            # Try int first
            return int(output)
        except:
            try:
                # Try float
                return float(output)
            except:
                pass

        # Try to parse as boolean
        if output.lower() in ('true', 'false'):
            return output.lower() == 'true'

        # Return as string
        return output

    except subprocess.TimeoutExpired:
        logger.error(f"Code execution timed out after {timeout} seconds")
        os.unlink(temp_file)
        raise Exception("Code execution timeout")
    except Exception as e:
        logger.error(f"Error executing code: {e}")
        if os.path.exists(temp_file):
            os.unlink(temp_file)
        raise
