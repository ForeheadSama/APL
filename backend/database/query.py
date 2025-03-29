from .connect import get_db_connection

from datetime import datetime
from typing import List, Dict, Any, Tuple, Optional
# from backend.database.query import get_or_create_user_id
# from backend.llm_integration.gemini_helper import fetch_events_from_gemini


def get_events_by_date(event_type: str, date: datetime.date) -> List[Dict[str, Any]]:
    """
    Fetch all events of a specific type on a specific date from the Events table.
    
    Args:
        event_type (str): Type of event to filter by (e.g., 'concert', 'movie')
        date (datetime.date): Date to filter events by
    
    Returns:
        List[Dict[str, Any]]: List of event dictionaries
    """
    events = []
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Query to get events of specific type on specific date
        query = """
        SELECT event_id, event_type, name, venue, date, price, available_tickets
        FROM Events
        WHERE event_type = ? AND CONVERT(date, date) = ?
        ORDER BY name
        """
        
        cursor.execute(query, (event_type, date))
        
        # Convert rows to dictionaries
        columns = [column[0] for column in cursor.description]
        for row in cursor.fetchall():
            event = dict(zip(columns, row))
            # Convert date to string format for easier handling
            event['date'] = event['date'].strftime('%B %d, %Y') if event['date'] else None
            events.append(event)
            
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Database error in get_events_by_date: {str(e)}")
    
    return events

def get_events_by_name(event_name: str) -> List[Dict[str, Any]]:
    """
    Fetch all events with a specific name from the Events table.
    
    Args:
        event_name (str): Name of the event to search for
    
    Returns:
        List[Dict[str, Any]]: List of event dictionaries
    """
    events = []
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Query to get events with specific name (using LIKE for partial matching)
        query = """
        SELECT event_id, event_type, name, venue, date, price, available_tickets
        FROM Events
        WHERE name LIKE ?
        ORDER BY date
        """
        
        cursor.execute(query, (f'%{event_name}%',))
        
        # Convert rows to dictionaries
        columns = [column[0] for column in cursor.description]
        for row in cursor.fetchall():
            event = dict(zip(columns, row))
            # Convert date to string format for easier handling
            event['date'] = event['date'].strftime('%B %d, %Y') if event['date'] else None
            events.append(event)
            
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Database error in get_events_by_name: {str(e)}")
    
    return events

def add_event(event_data: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Add a new event to the Events table if it doesn't already exist.
    
    Args:
        event_data (Dict[str, Any]): Dictionary containing event data
    
    Returns:
        Tuple[bool, str]: Success status and message
    """
    try:
        # Check if event already exists
        conn = get_db_connection()
        cursor = conn.cursor()
        
        check_query = """
        SELECT COUNT(*) 
        FROM Events 
        WHERE name = ? AND venue = ? AND CONVERT(date, date) = ?
        """
        
        # Convert date string to date object if needed
        event_date = event_data['date']
        if isinstance(event_date, str):
            try:
                event_date = datetime.datetime.strptime(event_date, '%B %d, %Y').date()
            except ValueError:
                return False, f"Invalid date format: {event_date}"
        
        cursor.execute(check_query, (event_data['name'], event_data['venue'], event_date))
        count = cursor.fetchone()[0]
        
        if count > 0:
            cursor.close()
            conn.close()
            return False, "Event already exists in database"
        
        # Insert new event
        insert_query = """
        INSERT INTO Events (event_type, name, venue, date, price, available_tickets)
        VALUES (?, ?, ?, ?, ?, ?)
        """
        
        cursor.execute(
            insert_query,
            (
                event_data['event_type'],
                event_data['name'],
                event_data['venue'],
                event_date,
                event_data['price'],
                event_data['available_tickets']
            )
        )
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return True, "Event added successfully"
        
    except Exception as e:
        return False, f"Error adding event: {str(e)}"

def check_event_exists(name: str, venue: str, date: datetime.date) -> bool:
    """
    Check if an event with the given name, venue, and date already exists.
    
    Args:
        name (str): Event name
        venue (str): Event venue
        date (datetime.date): Event date
    
    Returns:
        bool: True if event exists, False otherwise
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
        SELECT COUNT(*) 
        FROM Events 
        WHERE name = ? AND venue = ? AND CONVERT(date, date) = ?
        """
        
        cursor.execute(query, (name, venue, date))
        count = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        return count > 0
        
    except Exception as e:
        print(f"Error checking event existence: {str(e)}")
        return False

def check_available_tickets(event_id):
    """Check the number of available tickets for an event."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT available_tickets FROM Events WHERE event_id = ?", event_id)
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else 0

def check_event_price(event_id):
    """Check the price of an event."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT price FROM Events WHERE event_id = ?", event_id)
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def get_or_create_user_id(name):
    """
    Get the user ID for a given name. If the user doesn't exist, add them to the Users table.
    Args:
        name (str): The name of the user.
    Returns:
        int: The user ID.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Check if the user already exists
        cursor.execute("SELECT user_id FROM Users WHERE name = ?", (name,))
        result = cursor.fetchone()

        if result:
            # User exists, return their ID
            return result[0]
        else:
            # User doesn't exist, insert them into the Users table
            cursor.execute("INSERT INTO Users (name) VALUES (?)", (name,))
            conn.commit()

            # Get the newly generated user ID
            cursor.execute("SELECT user_id FROM Users WHERE name = ?", (name,))
            result = cursor.fetchone()
            return result[0]
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

# def book_ticket(quantity, user_name, date, event_name, event_type, venue, price, available_tickets):
#     """Book tickets for an event."""
#     conn = get_db_connection()
#     cursor = conn.cursor()
#     try:
#         # Get or create the user ID
#         user_id = get_or_create_user_id(user_name)

#         # Convert the date string to a datetime object
#         date_obj = datetime.strptime(date, "%B %d, %Y")  # Parse the date string
#         formatted_date = date_obj.strftime("%Y-%m-%d %H:%M:%S")  # Format for SQL DATETIME

#         # Get or create the event ID
#         #event_id = get_or_create_event_id(event_name, event_type, formatted_date, venue, price, available_tickets)

#         if event_id == "None":
#             return False, "Requested event does not exist yet, try another event."
            
#         # Check available tickets
#         available = check_available_tickets(event_id)
#         if available < quantity:
#             return False, "Not enough tickets available."

#         # Update available tickets
#         cursor.execute("UPDATE Events SET available_tickets = available_tickets - ? WHERE event_id = ?", (quantity, event_id))

#         # Insert booking
#         cursor.execute("""
#             INSERT INTO Bookings (event_id, user_id, quantity, date, status)
#             VALUES (?, ?, ?, ?, 'Pending')
#         """, (event_id, user_id, quantity, formatted_date))

#         conn.commit()
#         return True, "Booking successful."
    
#     except Exception as e:
#         conn.rollback()
#         return False, f"Error booking tickets: {e}"
#     finally:
#         conn.close()

def pay_for_booking(booking_id):
    """Mark a booking as paid."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Check if booking exists and is not already paid
        cursor.execute("SELECT status FROM Bookings WHERE booking_id = ?", booking_id)
        result = cursor.fetchone()
        if not result:
            return False, "Booking not found."
        if result[0] == "Paid":
            return False, "Booking is already paid."

        # Update booking status
        cursor.execute("UPDATE Bookings SET status = 'Paid' WHERE booking_id = ?", booking_id)
        conn.commit()
        return True, "Payment successful."
    except Exception as e:
        conn.rollback()
        return False, f"Error processing payment: {e}"
    finally:
        conn.close()

def cancel_booking(booking_id):
    """Cancel a booking."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Check if booking exists and is not already paid
        cursor.execute("SELECT status, event_id, quantity FROM Bookings WHERE booking_id = ?", booking_id)
        result = cursor.fetchone()
        if not result:
            return False, "Booking not found."
        if result[0] == "Paid":
            return False, "Cannot cancel a paid booking."

        # Add tickets back to available pool
        cursor.execute("UPDATE Events SET available_tickets = available_tickets + ? WHERE event_id = ?", (result[2], result[1]))

        # Delete booking
        cursor.execute("DELETE FROM Bookings WHERE booking_id = ?", booking_id)
        conn.commit()
        return True, "Cancellation successful."
    except Exception as e:
        conn.rollback()
        return False, f"Error canceling booking: {e}"
    finally:
        conn.close()