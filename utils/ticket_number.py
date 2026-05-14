# utils/ticket_number.py
#
# Generates ticket numbers like: TKT-2024-000001
# They are SERIAL — every number is one higher than the last.
# No gaps, no duplicates, even if the app restarts.
#
# How it works:
#   We store the last used number in the database itself.
#   Every new ticket reads that number, adds 1, saves it back.
#   This is called an "atomic increment" — safe even if two
#   staff members issue tickets at the same moment.

from database.connection import get_connection
import datetime


def get_next_ticket_number():
    """
    Returns the next serial ticket number as a string.
    Format: TKT-YYYY-NNNNNN   e.g. TKT-2024-000001

    This is the ONLY function that should ever create ticket numbers.
    Never generate them manually anywhere else.

    Returns:
        str → e.g. "TKT-2024-000042"
    """
    conn   = get_connection()
    cursor = conn.cursor()

    year = datetime.datetime.now().year

    # Lock the counter row so two staff can't grab the same number
    # FOR UPDATE = database-level lock, released after commit
    cursor.execute("""
        SELECT counter_value FROM ticket_counter
        WHERE year = %s
        FOR UPDATE
    """, (year,))
    row = cursor.fetchone()

    if row is None:
        # First ticket of the year — create the counter starting at 1
        cursor.execute(
            "INSERT INTO ticket_counter (year, counter_value) VALUES (%s, 1)",
            (year,)
        )
        number = 1
    else:
        # Increment the counter by 1
        number = row[0] + 1
        cursor.execute(
            "UPDATE ticket_counter SET counter_value = %s WHERE year = %s",
            (number, year)
        )

    conn.commit()
    cursor.close()
    conn.close()

    # Format: TKT-2024-000042 (always 6 digits, padded with zeros)
    return f"TKT-{year}-{str(number).zfill(6)}"