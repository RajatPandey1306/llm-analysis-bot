from langchain_core.tools import tool
import subprocess
import os

@tool
def run_code(code: str) -> dict:
    """
    Executes Python code in an isolated subprocess using uv.

    This tool:
      1. Takes in python code as input
      2. Writes code into a temporary .py file
      3. Executes the file using `uv run`
      4. Returns its output

    Parameters
    ----------
    code : str
        Python source code to execute.

    Returns
    -------
    dict
        {
            "stdout": <program output>,
            "stderr": <errors if any>,
            "return_code": <exit code>
        }
    """
    try:
        filename = "runner.py"
        os.makedirs("LLMFiles", exist_ok=True)

        # Strip code fences if present
        code = code.strip()
        if code.startswith("```"):
            code = code.split("\\n", 1)[1]
        if code.endswith("```"):
            code = code.rsplit("\\n", 1)[0]
        code = code.strip()

        with open(os.path.join("LLMFiles", filename), "w", encoding="utf-8") as f:
            f.write(code)

        proc = subprocess.Popen(
            ["uv", "run", filename],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd="LLMFiles"
        )
        stdout, stderr = proc.communicate()

        return {
            "stdout": stdout,
            "stderr": stderr,
            "return_code": proc.returncode
        }
    except Exception as e:
        return {
            "stdout": "",
            "stderr": str(e),
            "return_code": -1
        }
