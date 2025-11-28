"""
Test script to verify the endpoint works with the demo
"""

import requests
import json

# Configuration - UPDATE THESE
EMAIL = "21f3001699@ds.study.iitm.ac.in"
SECRET = "Cb350_RS"
ENDPOINT_URL = "http://localhost:8000/quiz"  # Change to your ngrok URL for remote testing

# Demo quiz URL
DEMO_URL = "https://tds-llm-analysis.s-anand.net/demo"


def test_endpoint():
    """Test the endpoint with demo quiz"""

    payload = {
        "email": EMAIL,
        "secret": SECRET,
        "url": DEMO_URL
    }

    print("Testing endpoint...")
    print(f"Sending request to: {ENDPOINT_URL}")
    print(f"Payload: {json.dumps(payload, indent=2)}")

    try:
        response = requests.post(
            ENDPOINT_URL,
            json=payload,
            timeout=10
        )

        print(f"\nResponse Status: {response.status_code}")
        print(f"Response Body: {json.dumps(response.json(), indent=2)}")

        if response.status_code == 200:
            print("\n✓ Endpoint accepted the request!")
            print("Check the server logs to see agent progress...")
        else:
            print(f"\n✗ Request failed with status {response.status_code}")

    except Exception as e:
        print(f"\n✗ Error: {e}")


def test_wrong_secret():
    """Test with wrong secret (should get 403)"""

    payload = {
        "email": EMAIL,
        "secret": "wrong_secret",
        "url": DEMO_URL
    }

    print("\n\nTesting with wrong secret...")

    try:
        response = requests.post(
            ENDPOINT_URL,
            json=payload,
            timeout=10
        )

        print(f"Response Status: {response.status_code}")

        if response.status_code == 403:
            print("✓ Correctly rejected invalid secret")
        else:
            print("✗ Expected 403 status code")

    except Exception as e:
        print(f"✗ Error: {e}")


def test_invalid_json():
    """Test with invalid JSON (should get 400)"""

    print("\n\nTesting with invalid JSON...")

    try:
        response = requests.post(
            ENDPOINT_URL,
            data="invalid json",
            headers={"Content-Type": "application/json"},
            timeout=10
        )

        print(f"Response Status: {response.status_code}")

        if response.status_code == 400:
            print("✓ Correctly rejected invalid JSON")
        else:
            print("✗ Expected 400 status code")

    except Exception as e:
        print(f"✗ Error: {e}")


if __name__ == "__main__":
    print("="*60)
    print("LLM Analysis Quiz - Endpoint Test")
    print("="*60)

    # Test 1: Valid request
    test_endpoint()

    # Test 2: Wrong secret
    test_wrong_secret()

    # Test 3: Invalid JSON
    test_invalid_json()

    print("\n" + "="*60)
    print("Testing complete!")
    print("="*60)
