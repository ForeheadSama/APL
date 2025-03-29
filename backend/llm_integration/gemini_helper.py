import os
import json
import datetime
import requests
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
import google.generativeai as genai

from backend.database.query import add_event, check_event_exists

# Load environment variables
load_dotenv()

# Configure Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro')

# Get Eventbrite API key
EVENTBRITE_API_KEY = os.getenv("EVENTBRITE_API_KEY")

def sync_events_from_eventbrite(event_type: Optional[str] = None) -> None:
    """
    Fetch events from Eventbrite API and store them in the database if they don't exist.
    Filter events to Jamaica only.
    
    Args:
        event_type (Optional[str]): Type of event to fetch (None for all types)
    """
    if not EVENTBRITE_API_KEY:
        print("Error: Eventbrite API key not found in environment variables.")
        return
    
    try:
        # Calculate today's date
        today = datetime.datetime.now().date()
        
        # Format today's date for Eventbrite API
        start_date = today.strftime('%Y-%m-%dT00:00:00')
        
        # Base URL for Eventbrite API
        url = "https://www.eventbriteapi.com/v3/events/search/"
        
        # Parameters for the API request
        params = {
            "token": EVENTBRITE_API_KEY,
            "location.address": "Jamaica",  # Filter events to Jamaica only
            "start_date.range_start": start_date,  # Fetch events from today onward
            "expand": "venue"
        }
        
        # Add search term if event_type is specified
        if event_type:

            # Use event_type as a search term instead of just a category filter
            params["q"] = event_type

            # Map event type to Eventbrite category ID
            category_map = {
                "concert": "103",  # Music category
                "movie": "104",    # Film & Media
                "theater": "105",  # Performing & Visual Arts
                "sports": "108",   # Sports & Fitness
                "conference": "101", # Business & Professional
                "party": "113",       # Social events
                "carnival": "113",    # Map carnival to social events too
            }
            
            if event_type.lower() in category_map:
                params["categories"] = category_map.get(event_type.lower())
        
        # Make the API request
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            events = data.get('events', [])
            
            # Process each event
            for event in events:
                # Extract event details
                try:
                    name = event.get('name', {}).get('text', 'Unnamed Event')
                    
                    # Skip events without venues in Jamaica
                    venue_obj = event.get('venue', {})
                    if not venue_obj:
                        continue
                    
                    venue_address = venue_obj.get('address', {})
                    country = venue_address.get('country', '')
                    if country.lower() != 'jm':  # Jamaica country code
                        continue
                    
                    venue_name = venue_obj.get('name', 'Unknown Venue')
                    
                    # Get event date
                    start_time = event.get('start', {}).get('local', '')
                    if not start_time:
                        continue
                    
                    start_date = datetime.datetime.strptime(start_time.split('T')[0], '%Y-%m-%d').date()
                    formatted_date = start_date.strftime('%B %d, %Y')
                    
                    # Determine event type from category
                    category_id = event.get('category_id', '')
                    determined_event_type = "general"
                    
                    # Reverse lookup of category map
                    category_map_reverse = {v: k for k, v in category_map.items()}
                    if category_id in category_map_reverse:
                        determined_event_type = category_map_reverse[category_id]
                    
                    # If event_type parameter was provided, use that instead
                    final_event_type = event_type if event_type else determined_event_type
                    
                    # Get price (if available, otherwise use default)
                    is_free = event.get('is_free', False)
                    price = 0.0 if is_free else 20.0  # Default price
                    
                    # Get available tickets (use a default value since Eventbrite API doesn't provide this)
                    available_tickets = 100  # Default value
                    
                    # Create event data dictionary
                    event_data = {
                        'event_type': final_event_type,
                        'name': name,
                        'venue': venue_name,
                        'date': formatted_date,
                        'price': price,
                        'available_tickets': available_tickets
                    }
                    
                    # Add event to database if it doesn't exist
                    if not check_event_exists(name, venue_name, start_date):
                        add_event(event_data)
                
                except Exception as e:
                    print(f"Error processing event: {str(e)}")
                    continue
            
            print(f"Successfully synced events from Eventbrite to database.")
    
    except Exception as e:
        print(f"Error in sync_events_from_eventbrite: {str(e)}")

def format_events_list(events: List[Dict[str, Any]]) -> str:
    """
    Use Gemini to format a list of events in a user-friendly way.
    
    Args:
        events (List[Dict[str, Any]]): List of event dictionaries
    
    Returns:
        str: Formatted events list
    """
    try:
        # Prepare events data for Gemini
        events_json = json.dumps(events, indent=2)
        
        # Create prompt for Gemini
        prompt = f"""
        Format the following list of events in a neat, readable, and user-friendly way.
        Make it visually appealing with proper spacing and organization.
        
        Events data:
        {events_json}
        
        Format each event to show:
        1. Event name (bold or highlighted)
        2. Venue
        3. Date
        4. Price
        5. Available tickets
        
        Add a nice header and make the output easy to read.
        """
        
        # Generate response from Gemini
        response = model.generate_content(prompt)
        
        # Return the formatted text
        return response.text
    
    except Exception as e:
        print(f"Error formatting events with Gemini: {str(e)}")
        
        # Fallback formatting if Gemini fails
        formatted_text = "EVENTS LIST:\n\n"
        for event in events:
            formatted_text += f"EVENT: {event.get('name', 'Unnamed')}\n"
            formatted_text += f"Venue: {event.get('venue', 'Unknown')}\n"
            formatted_text += f"Date: {event.get('date', 'Not specified')}\n"
            formatted_text += f"Price: ${event.get('price', 0.0)}\n"
            formatted_text += f"Available Tickets: {event.get('available_tickets', 0)}\n"
            formatted_text += "-" * 40 + "\n"
        
        return formatted_text

def format_event_details(events: List[Dict[str, Any]]) -> str:
    """
    Use Gemini to format detailed information about events in a user-friendly way.
    
    Args:
        events (List[Dict[str, Any]]): List of event dictionaries
    
    Returns:
        str: Formatted event details
    """
    try:
        # Prepare events data for Gemini
        events_json = json.dumps(events, indent=2)
        
        # Create prompt for Gemini
        prompt = f"""
        Format the following event(s) details in a comprehensive, readable, and user-friendly way.
        Make it visually appealing with proper spacing and organization.
        
        Events data:
        {events_json}
        
        For each event, provide a detailed presentation including:
        1. Event name (bold or highlighted)
        2. Event type
        3. Venue location
        4. Date and time
        5. Ticket price (formatted as currency)
        6. Available tickets
        
        Add a descriptive header and organize the information in a clear, easy-to-read layout.
        If there are multiple events, separate them clearly.
        """
        
        # Generate response from Gemini
        response = model.generate_content(prompt)
        
        # Return the formatted text
        return response.text
    
    except Exception as e:
        print(f"Error formatting event details with Gemini: {str(e)}")
        
        # Fallback formatting if Gemini fails
        if len(events) == 1:
            event = events[0]
            formatted_text = f"EVENT DETAILS: {event.get('name', 'Unnamed')}\n\n"
            formatted_text += f"Type: {event.get('event_type', 'Not specified')}\n"
            formatted_text += f"Venue: {event.get('venue', 'Unknown')}\n"
            formatted_text += f"Date: {event.get('date', 'Not specified')}\n"
            formatted_text += f"Price: ${event.get('price', 0.0)}\n"
            formatted_text += f"Available Tickets: {event.get('available_tickets', 0)}\n"
        else:
            formatted_text = "MULTIPLE EVENTS FOUND:\n\n"
            for i, event in enumerate(events, 1):
                formatted_text += f"EVENT #{i}: {event.get('name', 'Unnamed')}\n"
                formatted_text += f"Type: {event.get('event_type', 'Not specified')}\n"
                formatted_text += f"Venue: {event.get('venue', 'Unknown')}\n"
                formatted_text += f"Date: {event.get('date', 'Not specified')}\n"
                formatted_text += f"Price: ${event.get('price', 0.0)}\n"
                formatted_text += f"Available Tickets: {event.get('available_tickets', 0)}\n"
                formatted_text += "-" * 40 + "\n"
        
        return formatted_text