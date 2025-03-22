from .connect import get_db_connection

from datetime import datetime
from backend.database.query import get_or_create_user_id

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

def get_or_create_event_id(event_name, event_type, date, venue, price, available_tickets):
    """
    Get the event ID for a given event name. If the event doesn't exist, add it to the Events table.
    Args:
        event_name (str): The name of the event.
        event_type (str): The type of the event (e.g., concert, movie, bus).
        date (str): The date of the event in 'YYYY-MM-DD HH:MM:SS' format.
        venue (str): The venue of the event.
        price (float): The price of the event.
        available_tickets (int): The number of available tickets.
    Returns:
        int: The event ID.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Check if the event already exists
        cursor.execute("SELECT event_id FROM Events WHERE name = ?", (event_name,))
        result = cursor.fetchone()

        if result:
            # Event exists, return its ID
            return result[0]
        else:
            # Event doesn't exist, insert it into the Events table
            cursor.execute("""
                INSERT INTO Events (event_type, name, venue, date, price, available_tickets)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (event_type, event_name, venue, date, price, available_tickets))
            conn.commit()

            # Get the newly generated event ID
            cursor.execute("SELECT event_id FROM Events WHERE name = ?", (event_name,))
            result = cursor.fetchone()
            return result[0]
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def book_ticket(quantity, user_name, date, event_name, event_type, venue, price, available_tickets):
    """Book tickets for an event."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Get or create the user ID
        user_id = get_or_create_user_id(user_name)

        # Convert the date string to a datetime object
        date_obj = datetime.strptime(date, "%B %d, %Y")  # Parse the date string
        formatted_date = date_obj.strftime("%Y-%m-%d %H:%M:%S")  # Format for SQL DATETIME

        # Get or create the event ID
        event_id = get_or_create_event_id(event_name, event_type, formatted_date, venue, price, available_tickets)

        # Check available tickets
        available = check_available_tickets(event_id)
        if available < quantity:
            return False, "Not enough tickets available."

        # Update available tickets
        cursor.execute("UPDATE Events SET available_tickets = available_tickets - ? WHERE event_id = ?", (quantity, event_id))

        # Insert booking
        cursor.execute("""
            INSERT INTO Bookings (event_id, user_id, quantity, date, status)
            VALUES (?, ?, ?, ?, 'Pending')
        """, (event_id, user_id, quantity, formatted_date))

        conn.commit()
        return True, "Booking successful."
    
    except Exception as e:
        conn.rollback()
        return False, f"Error booking tickets: {e}"
    finally:
        conn.close()

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