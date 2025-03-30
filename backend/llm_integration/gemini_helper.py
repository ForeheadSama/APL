import os
import json
from datetime import datetime, date
import requests

from typing import List, Dict, Any, Optional
from pathlib import Path
from dotenv import load_dotenv
from backend.database.query import get_events_by_name

import google.generativeai as genai

from backend.database.query import add_event, check_event_exists, get_events_by_date

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

try:
    GEMINI_API_KEY = get_api_key("GEMINI_API_KEY", 39)
    TICKETMASTER_API_KEY = get_api_key("TICKETMASTER_API_KEY", 32)
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')

except ValueError as e:
    raise RuntimeError(f"API configuration failed: {str(e)}")


def fetch_events_from_ticketmaster(
    event_type: Optional[str] = None, 
    event_name: Optional[str] = None
    ) -> List[Dict[str, Any]]:

    """
    Fetch events from Ticketmaster API with robust error handling
    Returns empty list on failure to allow database fallback
    """

    #today = datetime.now().date()
    
    params = {
        "apikey": TICKETMASTER_API_KEY,
        "size": 50,
    }

    # Handle event type/name parameters 
    if event_type:
        params["classificationName"] = event_type.lower()  # Use lowercase for consistency
    if event_name:
        params["keyword"] = event_name.replace('"', '')  # Remove quotes if present

    try:
        response = requests.get(
            "https://app.ticketmaster.com/discovery/v2/events.json",
            params=params,
            timeout=10
        )
        response.raise_for_status()
        return _process_ticketmaster_events(response.json())
        
    except requests.exceptions.HTTPError as e:
        if response.status_code == 400:
            print(f"Ticketmaster API rejected our parameters: {params}")
        return []

def _process_ticketmaster_events(events_data: dict) -> List[Dict[str, Any]]:
    """Process raw Ticketmaster API response"""
    events = []

    today = date.today()
    
    for event in events_data.get('_embedded', {}).get('events', []):
        try:
            venue = event.get('_embedded', {}).get('venues', [{}])[0]
            if not venue:
                continue
                
            # Parse date
            start_date = event.get('dates', {}).get('start', {}).get('localDate')
            if not start_date:
                continue
                
            event_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            if event_date < today:
                continue
                
            # Extract price properly
            price_ranges = event.get('priceRanges', [{}])
            price = price_ranges[0].get('min', 0.0) if price_ranges else 0.0
            
            event_data = {
                'event_type': event.get('classifications', [{}])[0]
                              .get('segment', {}).get('name', 'general').lower(),
                'name': event.get('name', 'Unnamed Event'),
                'venue': venue.get('name', 'Unknown Venue'),
                'date': event_date.strftime('%B %d, %Y'),  # Convert to preferred format
                'price': float(price),
                'available_tickets': 100
            }
            
            # Add to database
            add_event(event_data)
                
            events.append(event_data)
            
        except Exception as e:
            print(f"Skipping malformed event: {str(e)}")
            continue
            
    return events

# 4. Unified event fetcher with fallback
def get_and_format_events(
    event_type: Optional[str] = None,
    event_name: Optional[str] = None,
    date: Optional[str] = None
    ) -> str:

    """
    Unified interface for getting events with:
    - Ticketmaster API as primary source
    - Database as fallback
    - Automatic Gemini formatting
    """
    # Clean input parameters
    event_name = event_name.strip('"').strip("'") if event_name else None
    event_type = event_type.lower() if event_type else None

    try:
        # Try API first
        api_events = fetch_events_from_ticketmaster(event_type, event_name)
        
        # Fallback to database if needed
        db_events = []

        if event_name:
            db_events = get_events_by_name(event_name)

        elif event_type and date:
            try:
                date_obj = datetime.datetime.strptime(date, '%B %d, %Y').date()
                if date_obj >= datetime.datetime.now().date():
                    db_events = get_events_by_date(event_type, date_obj)
            except ValueError:
                pass

        all_events = api_events + [e for e in db_events if e not in api_events]
        
        if not all_events:
            if event_name:
                return f"No events found matching '{event_name}'"
            
            elif event_type and date:
                return f"No {event_type} events found on {date}"
            
            return "No upcoming events found"
            
        return format_events(all_events)

    except Exception as e:
        print(f"System error: {str(e)}")
        return "Event search is temporarily unavailable."

def _get_db_events(
    event_type: Optional[str],
    event_name: Optional[str],
    date: Optional[str]
) -> List[Dict[str, Any]]:
    
    """Get events from database with date validation"""
    if date:
        try:
            date_obj = datetime.datetime.strptime(date, '%B %d, %Y').date()
            if date_obj < datetime.datetime.now().date():
                return []
            return get_events_by_date(event_type, date_obj) if event_type else []
        except ValueError:
            return []
    return get_events_by_name(event_name) if event_name else []

def _generate_empty_message(
    event_type: Optional[str],
    event_name: Optional[str],
    date: Optional[str]
) -> str:
    """Generate appropriate 'not found' message"""
    if event_type and date:
        return f"No {event_type} events found on {date}"
    if event_name:
        return f"No events found matching '{event_name}'"
    return "No upcoming events found"

def format_events(events: List[Dict[str, Any]]) -> str:
    """Format events using Gemini with Markdown fallback"""
    if len(events) == 1:
        return _format_with_gemini(
            "Create a detailed event description with:",
            events[0],
            ["name", "event_type", "venue", "date", "price"]
        )
    return _format_with_gemini(
        "Create a bulleted list of events including:",
        events,
        ["name", "venue", "date"]
    )

import json
from decimal import Decimal
from typing import Any, List

def _format_with_gemini(instruction: str, data: Any, fields: List[str]) -> str:
    """Generic Gemini formatter with proper Decimal handling and robust error handling"""
    
    def decimal_serializer(obj):
        """Custom serializer for Decimal objects"""
        if isinstance(obj, Decimal):
            return float(obj)  # Convert Decimal to float for JSON
        elif hasattr(obj, 'isoformat'):  # Handle date/datetime objects
            return obj.isoformat()
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
    
    try:
        # Convert data to JSON with custom serialization
        json_data = json.dumps(
            data,
            indent=2,
            default=decimal_serializer,
            ensure_ascii=False
        )
        
        prompt = f"{instruction}\n{json_data}\nFocus on: {', '.join(fields)}"
        response = model.generate_content(prompt)

        return response.text
        
    except Exception as e:
        print(f"Gemini formatting failed: {str(e)}")

        try:
            # Attempt fallback with simplified data
            simplified_data = {
                field: decimal_serializer(data[field]) if field in data else ""
                for field in fields
            }
            return _fallback_format(simplified_data, fields)
        
        except Exception as fallback_error:
            print(f"Fallback formatting also failed: {str(fallback_error)}")
            return "Could not format event information"

def _fallback_format(data: Any, fields: List[str]) -> str:
    """Basic formatting when Gemini fails"""
    if isinstance(data, list):
        return "\n".join(
            " | ".join(str(item.get(field, "")) for field in fields)
            for item in data
        )
    return "\n".join(f"{field}: {data.get(field, '')}" for field in fields)