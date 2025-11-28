from langchain_core.tools import tool
import subprocess

@tool
def add_dependencies(package_name: str) -> str:
    """
    Dynamically install a Python package using uv.

    Use this when you need a package that isn't already installed.
    The package will be added to the project and immediately available.

    Parameters
    ----------
    package_name : str
        Name of the package to install (e.g., "pandas", "numpy").

    Returns
    -------
    str
        Success or error message.
    """
    try:
        print(f"\\nInstalling package: {package_name}")

        result = subprocess.run(
            ["uv", "add", package_name],
            capture_output=True,
            text=True,
            timeout=60
        )

        if result.returncode == 0:
            return f"Successfully installed {package_name}"
        else:
            return f"Error installing {package_name}: {result.stderr}"

    except Exception as e:
        return f"Error: {str(e)}"
