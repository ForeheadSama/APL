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
        ORDER BY event_type, name
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
    Robust event addition with proper date and price handling
    """
    conn = None
    try:
        # Convert and validate date
        date_str = event_data['date']
        try:
            event_date = datetime.strptime(date_str, '%B %d, %Y').date()
        except ValueError as e:
            return False, f"Invalid date format: {date_str}. Expected 'Month Day, Year' (e.g. 'June 15, 2025')"

        # Get proper price (default to 0.0 if not available)
        price = float(event_data.get('price', 0.0))
        
        conn = get_db_connection()
        cursor = conn.cursor()

        # Check for existing event
        cursor.execute("""
            SELECT COUNT(*) 
            FROM Events 
            WHERE LOWER(name) = LOWER(?) 
            AND LOWER(venue) = LOWER(?) 
            AND date = ?
            """,
            (
                event_data['name'].strip(),
                event_data['venue'].strip(),
                event_date
            )
        )

        if cursor.fetchone()[0] > 0:
            return False, "Event already exists"

        # Insert new event
        cursor.execute("""
            INSERT INTO Events 
            (event_type, name, venue, date, price, available_tickets)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                event_data['event_type'].strip().lower(),
                event_data['name'].strip(),
                event_data['venue'].strip(),
                event_date,
                price,
                int(event_data.get('available_tickets', 100))
            )
        )

        conn.commit()
        return True, "Event added successfully"

    except Exception as e:
        if conn:
            conn.rollback()
        return False, f"Database error: {str(e)}"
    finally:
        if conn:
            conn.close()

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

from datetime import datetime, date
from decimal import Decimal

def book_tickets(quantity: int, user_name: str, event_date: str, event_name: str) -> tuple[bool, str]:
    """Book tickets for an event with comprehensive validation"""
    conn = None
    try:
        # Validate quantity
        if not isinstance(quantity, int) or quantity <= 0:
            return False, "Number of tickets to book must be a positive integer."

        # Validate and parse date
        try:
            booking_date = datetime.strptime(event_date, "%B %d, %Y").date()
            if booking_date < date.today():
                return False, "Cannot book tickets for past dates. Try a date in the future."
            sql_date = booking_date.strftime("%Y-%m-%d")
        except ValueError:
            return False, "Invalid date format. Use 'Month Day, Year' (e.g. 'June 15, 2025')"

        conn = get_db_connection()
        cursor = conn.cursor()

        # Get or create user
        cursor.execute("SELECT user_id FROM Users WHERE name = ?", (user_name,))
        user = cursor.fetchone()
        if not user:
            cursor.execute("INSERT INTO Users (name) OUTPUT INSERTED.user_id VALUES (?)", (user_name,))
            user_id = cursor.fetchone()[0]
            conn.commit()
        else:
            user_id = user[0]

        # Find matching event
        cursor.execute("""
            SELECT event_id, price, available_tickets 
            FROM Events 
            WHERE name = ? 
            AND CONVERT(date, date) = ?
            """, 
            (event_name, sql_date))
        event = cursor.fetchone()

        if not event:
            return False, f"Unfortunately, no event named '{event_name}' was found on {event_date}."

        event_id, price_per_ticket, available_tickets = event

        # Check ticket availability
        if available_tickets < quantity:
            return False, f"Only {available_tickets} tickets are available (requested: {quantity})"

        # Calculate total price
        total_price = Decimal(price_per_ticket) * quantity

        # Start transaction
        try:
            # Update available tickets
            cursor.execute("""
                UPDATE Events 
                SET available_tickets = available_tickets - ? 
                WHERE event_id = ? AND available_tickets >= ?
                """, 
                (quantity, event_id, quantity))
            
            if cursor.rowcount == 0:
                return False, "Unfortunately, tickets are no longer available"

            # Create booking
            cursor.execute("""
                INSERT INTO Bookings 
                (event_id, user_id, date, quantity, price, status)
                VALUES (?, ?, GETDATE(), ?, ?, 'Confirmed')
                """,
                (event_id, user_id, quantity, float(total_price)))
            
            conn.commit()
            return True, f"Successfully booked {quantity} ticket(s) for {user_name} to {event_name}! Be sure to pay for tickets using the PAY command to finalize your spot."

        except Exception as e:
            conn.rollback()
            return False, f"Booking failed: {str(e)}"

    except Exception as e:
        return False, f"System error: {str(e)}"
    finally:
        if conn:
            conn.close()

def pay_for_booking(event_name: str, user_name: str) -> tuple[bool, str]:
    """Mark a booking as paid after validating all conditions"""
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Verify user exists or create them
        cursor.execute("SELECT user_id FROM Users WHERE name = ?", (user_name,))
        user = cursor.fetchone()
        
        if not user:
            # User doesn't exist, create them
            cursor.execute("INSERT INTO Users (name) VALUES (?)", (user_name,))
            conn.commit()

            cursor.execute("SELECT user_id FROM Users WHERE name = ?", (user_name,))
            user = cursor.fetchone()

        user_id = user[0]

        # Find matching booking that isn't paid
        # Get most recent booking if multiple exist
        cursor.execute("""
            SELECT b.booking_id, b.status
            FROM Bookings b
            JOIN Events e ON b.event_id = e.event_id
            WHERE e.name = ? AND b.user_id = ?
            ORDER BY b.date DESC 
            """, 
            (event_name, user_id))
        
        booking = cursor.fetchone()

        # Handle all validation cases
        if not booking:
            return False, f"No booking found for '{event_name}' under '{user_name}'. Try booking first."
        
        booking_id, status = booking
        
        if status == "Paid":
            return False, f"Booking for '{event_name}' is already paid."
        
        if status == "Cancelled":
            return False, f"Cannot pay for cancelled booking. Try booking again."

        # Process payment
        cursor.execute("""
            UPDATE Bookings 
            SET status = 'Paid' 
            WHERE booking_id = ?
            """, 
            (booking_id,))
        
        conn.commit()
        return True, f"Payment for '{event_name}' confirmed!"

    except Exception as e:
        if conn:
            conn.rollback()
        return False, f"Payment processing failed: {str(e)}"
    finally:
        if conn:
            conn.close()

def cancel_booking(quantity: int, user_name: str, event_name: str) -> tuple[bool, str]:
    """Cancel booking(s) for a specific user and event.
    Args:
        quantity: Number of tickets to cancel
        user_name: Name of the user who made the booking
        event_name: Name of the event to cancel
    Returns:
        Tuple of (success: bool, message: str)
    """
    conn = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Get user ID
        cursor.execute("SELECT user_id FROM Users WHERE name = ?", (user_name,))
        user = cursor.fetchone()

        if not user:
            return False, f"User '{user_name}' not found."
        user_id = user[0]

        # Find the most recent matching booking that isn't paid
        cursor.execute("""
            SELECT b.booking_id, b.event_id, b.quantity, b.status, e.name
            FROM Bookings b
            JOIN Events e ON b.event_id = e.event_id
            WHERE b.user_id = ? AND e.name = ? AND b.status != 'Paid'
            ORDER BY b.date DESC
            """, (user_id, event_name))
        
        booking = cursor.fetchone()
        
        if not booking:
            return False, f"Unfortunately, no cancellable bookings were found for {user_name} to {event_name}."

        booking_id, event_id, booked_quantity, status, event_name = booking

        # Validate quantity
        if quantity > booked_quantity:
            return False, f"Cannot cancel {quantity} tickets. Only {booked_quantity} tickets were booked."

        # Update available tickets (add back the canceled quantity)
        cursor.execute("""
            UPDATE Events 
            SET available_tickets = available_tickets + ? 
            WHERE event_id = ?
            """, (quantity, event_id))

        # If canceling all tickets, delete the booking
        if quantity == booked_quantity:
            cursor.execute("DELETE FROM Bookings WHERE booking_id = ?", (booking_id,))
            message = f"Successfully canceled all {quantity} tickets for {event_name}."
        else:
            # If partial cancellation, update the booking quantity
            cursor.execute("""
                UPDATE Bookings 
                SET quantity = quantity - ? 
                WHERE booking_id = ?
                """, (quantity, booking_id))
            message = f"Successfully canceled {quantity} of {booked_quantity} tickets for {event_name}."

        conn.commit()
        return True, message

    except Exception as e:
        if conn:
            conn.rollback()
        return False, f"Error canceling booking: {str(e)}"
    finally:
        if conn:
            conn.close()