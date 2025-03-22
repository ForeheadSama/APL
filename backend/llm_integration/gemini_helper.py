import os
import google.generativeai as genai
import json
import re
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

# Initialize the Gemini model
model = genai.GenerativeModel('gemini-1.5-flash')

def fetch_events_from_gemini(event_type, date_str):
    """
    Fetch event information using Google's Gemini API.
    Args:
        event_type (str): Type of event (e.g., "concert", "movie", "flight").
        date_str (str): Date for the event (e.g., "2023-12-25").
    Returns:
        list: A list of events with details.
    """
    try:
        # Create a prompt for Gemini
        prompt = f"List real {event_type} events occurring on {date_str}. "
        prompt += "Format the response as a JSON array with each event having fields: "
        prompt += "name, venue, time, description. Include only 5 events and be factual. "
        prompt += "Make sure the response is valid JSON."

        # Generate content using Gemini
        response = model.generate_content(prompt)

        # Extract JSON from the response
        try:
            # First try to find JSON within triple backticks
            json_match = re.search(r'```json\n(.+?)\n```', response.text, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                # Otherwise, take the whole text as JSON
                json_str = response.text

            # Parse JSON
            events_data = json.loads(json_str)
            return events_data
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
            print(f"Response text: {response.text}")
            return []
    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        return []