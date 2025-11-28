from langchain_core.tools import tool
import requests
import json
import os
from typing import Any, Dict, Optional

@tool
def post_request(url: str, payload: Dict[str, Any], headers: Optional[Dict[str, str]] = None) -> Any:
    """
    Send an HTTP POST request to the given URL with the provided payload.

    This function is designed for LangGraph applications, where it can be wrapped
    as a Tool or used inside a Runnable to call external APIs, webhooks, or backend
    services during graph execution.

    IMPORTANT: This tool automatically injects the email and secret credentials
    into the payload for quiz submissions. You do not need to add these fields manually.

    REMEMBER: This a blocking function so it may take a while to return. Wait for the response.

    Args:
        url (str): The endpoint to send the POST request to.
        payload (Dict[str, Any]): The JSON-serializable request body (without email/secret).
        headers (Optional[Dict[str, str]]): Optional HTTP headers to include
            in the request. If omitted, a default JSON header is applied.

    Returns:
        Any: The response body. If the server returns JSON, a parsed dict is
        returned. Otherwise, the raw text response is returned.

    Raises:
        requests.HTTPError: If the server responds with an unsuccessful status.
        requests.RequestException: For network-related errors.
    """
    # Automatically inject credentials from environment variables
    email = os.getenv("MY_EMAIL")
    secret = os.getenv("MY_SECRET")

    # Add credentials to payload if not already present
    if email and "email" not in payload:
        payload["email"] = email
    if secret and "secret" not in payload:
        payload["secret"] = secret

    headers = headers or {"Content-Type": "application/json"}
    try:
        print(f"\\nSending Answer \\n{json.dumps(payload, indent=4)}\\n to url: {url}")
        response = requests.post(url, json=payload, headers=headers, timeout=30)

        # Raise on 4xx/5xx
        response.raise_for_status()

        # Try to return JSON, fallback to raw text
        data = response.json()
        delay = data.get("delay", 0)
        delay = delay if isinstance(delay, (int, float)) else 0
        correct = data.get("correct")

        # Remove URL if incorrect and still have time
        if not correct and delay < 180:
            if "url" in data:
                del data["url"]

        # If time expired, only return URL
        if delay >= 180:
            data = {
                "url": data.get("url")
            }

        print("Got the response: \\n", json.dumps(data, indent=4), '\\n')
        return data

    except requests.HTTPError as e:
        # Extract server's error response
        err_resp = e.response

        try:
            err_data = err_resp.json()
        except ValueError:
            err_data = err_resp.text

        print("HTTP Error Response:\\n", err_data)
        return err_data

    except Exception as e:
        print("Unexpected error:", e)
        return str(e)
