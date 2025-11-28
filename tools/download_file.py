from langchain_core.tools import tool
import requests
import os

@tool
def download_file(url: str, filename: str = None) -> str:
    """
    Download a file from a URL and save it to the LLMFiles directory.

    Use this tool for direct file downloads (PDFs, CSVs, images, etc.).
    DO NOT use get_rendered_html for file URLs.

    Parameters
    ----------
    url : str
        The URL of the file to download.
    filename : str, optional
        The name to save the file as. If not provided, extracts from URL.

    Returns
    -------
    str
        The saved filename (relative to LLMFiles directory).
    """
    try:
        print(f"\\nDownloading file from: {url}")

        # Make directory if needed
        os.makedirs("LLMFiles", exist_ok=True)

        # Get filename from URL if not provided
        if not filename:
            filename = url.split("/")[-1].split("?")[0]

        # Download file
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        # Save to LLMFiles
        filepath = os.path.join("LLMFiles", filename)
        with open(filepath, "wb") as f:
            f.write(response.content)

        print(f"Saved to: {filepath}")
        return filename

    except Exception as e:
        return f"Error downloading file: {str(e)}"
