import os
import re
from dotenv import load_dotenv
from pathlib import Path

# 1. Nuclear option for path resolution
SCRIPT_DIR = Path(__file__).parent.absolute()
os.chdir(SCRIPT_DIR)  # Force working directory

# 2. Load .env with verification
load_dotenv(override=True)
print(f"\nCurrent directory: {os.getcwd()}")
print(f".env exists: {Path('.env').exists()}")

# 3. Debug ALL environment variables
print("\nAll Environment Variables:")
for k, v in os.environ.items():
    if "TICKET" in k or "API" in k:
        print(f"  {k.ljust(20)} = '{v}' (Length: {len(v)})")

# 4. Advanced key extraction
def get_api_key():
    key = os.getenv("TICKETMASTER_API_KEY", "").strip()
    
    # Remove invisible characters
    key = re.sub(r'[^\x20-\x7E]', '', key)
    
    # Validate key format
    if not re.match(r'^[a-zA-Z0-9]{32}$', key):
        print(f"\n⚠️ Key format invalid! Detected: '{key}'")
        print("Try manually retyping the key in .env")
        return None
    return key

# 5. Test the key
if __name__ == "__main__":
    import requests
    
    API_KEY = get_api_key()
    if not API_KEY:
        exit(1)

    print(f"\nTesting key: {API_KEY[:4]}...{API_KEY[-4:]}")
    response = requests.get(
        "https://app.ticketmaster.com/discovery/v2/events.json",
        params={"apikey": API_KEY, "countryCode": "US", "size": 1}
    )

    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print("✅ Success! Key works")
    else:
        print("❌ Failed. Response:")
        print(response.text)