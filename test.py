import os
import requests
from dotenv import load_dotenv
from pathlib import Path

def load_env_safely():
    """Ensure .env is loaded from correct location"""
    env_path = Path(__file__).parent.parent.parent / '.env'
    load_dotenv(dotenv_path=env_path, override=True)

load_env_safely()

def get_api_key(key_name: str, expected_length: int) -> str:
    """Safely get and validate API keys"""
    key = os.getenv(key_name, "").strip()
    if not key or len(key) != expected_length:
        raise ValueError(f"Invalid {key_name} in .env")
    return key

def test_ticketmaster_connection():

    TICKETMASTER_API_KEY = get_api_key("TICKETMASTER_API_KEY", 32)
    try:
        response = requests.get(
            "https://app.ticketmaster.com/discovery/v2/events.json",
            params={"apikey": TICKETMASTER_API_KEY, "size": 1},
            timeout=5
        )
        print(f"API Response Status: {response.status_code}")
        print(f"Response Headers: {response.headers}")
        return True
    except Exception as e:
        print(f"API Connection Failed: {str(e)}")
        return False

# Call this at the start of get_and_format_events()
print("\n=== Connection Test ===")
test_ticketmaster_connection()
print("======================\n")