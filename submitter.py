"""
Answer Submission Handler
Posts answers to the quiz submission endpoint and handles responses
"""

import requests
import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)


async def submit_answer(
    submit_url: str,
    email: str,
    secret: str,
    quiz_url: str,
    answer: Any,
    timeout: int = 30
) -> Dict:
    """
    Submit answer to the quiz endpoint

    Args:
        submit_url: URL to submit the answer to
        email: Student email
        secret: Student secret
        quiz_url: Original quiz URL
        answer: The answer (can be bool, int, str, dict, etc.)
        timeout: Request timeout in seconds

    Returns:
        Response dictionary with 'correct', 'url', 'reason', etc.
    """
    logger.info(f"Submitting answer to {submit_url}")

    # Ensure answer is a primitive type (str, int, float, bool)
    # The server (D1) doesn't support nested JSON objects
    import json
    if isinstance(answer, (dict, list)):
        answer = json.dumps(answer)

    payload = {
        "email": email,
        "secret": secret,
        "url": quiz_url,
        "answer": answer
    }

    logger.info(f"Payload: {payload}")

    try:
        response = requests.post(
            submit_url,
            json=payload,
            timeout=timeout,
            headers={"Content-Type": "application/json"}
        )

        logger.info(f"Response status: {response.status_code}")
        logger.info(f"Response body: {response.text}")

        # Parse response
        if response.status_code == 200:
            result = response.json()

            if result.get("correct"):
                logger.info("✓ Answer is CORRECT!")
            else:
                logger.warning(f"✗ Answer is INCORRECT: {result.get('reason', 'No reason provided')}")

            return result
        else:
            logger.error(f"Submission failed with status {response.status_code}")
            return {
                "correct": False,
                "reason": f"HTTP {response.status_code}: {response.text}"
            }

    except Exception as e:
        logger.error(f"Error submitting answer: {e}")
        return {
            "correct": False,
            "reason": f"Submission error: {str(e)}"
        }


async def handle_response(response: Dict, max_retries: int = 2) -> Dict:
    """
    Handle the submission response

    Args:
        response: Response from submit_answer
        max_retries: Maximum number of retries for incorrect answers

    Returns:
        Dictionary with next actions
    """
    if response.get("correct"):
        # Success! Check if there's a next URL
        next_url = response.get("url")
        if next_url:
            logger.info(f"Moving to next quiz: {next_url}")
            return {"action": "continue", "url": next_url}
        else:
            logger.info("Quiz completed successfully!")
            return {"action": "complete"}
    else:
        # Incorrect answer
        reason = response.get("reason", "Unknown error")
        next_url = response.get("url")

        if next_url:
            # Can skip to next question
            logger.info(f"Incorrect, but can skip to: {next_url}")
            return {"action": "skip", "url": next_url, "reason": reason}
        else:
            # Can retry
            logger.info("Incorrect, can retry")
            return {"action": "retry", "reason": reason}
