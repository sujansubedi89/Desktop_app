# database/crud.py
# ─────────────────────────────────────────────────────────────────
# ALL database operations live here.
# Your friend imports from this file only — he never writes SQL.
#
# Sections:
#   A. Tourist functions
#   B. Ticket functions  (includes QR + serial number)
#   C. Checkpost entry functions
#   D. Lookup helpers    (dropdowns)
#   E. Dashboard stats
# ─────────────────────────────────────────────────────────────────

from database.connection import get_connection
from utils.ticket_number import get_next_ticket_number
from utils.qr_generator  import generate_qr, get_qr_path
import datetime


# ═══════════════════════════════════════════════
#  A. TOURIST FUNCTIONS
# ═══════════════════════════════════════════════

def create_tourist(full_name, passport_no, nationality, country_id=None):
    """
    Registers a new tourist.

    Parameters:
        full_name   (str) : "Priya Sharma"
        passport_no (str) : "IN998877"  — must be unique
        nationality (str) : "India"
        country_id  (int) : ID from countries table

    Returns:
        int  → new tourist's ID
        None → if passport already registered

    Example:
        tid = create_tourist("John Smith", "US123456", "USA", 3)
    """
    conn   = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO tourists (full_name, passport_no, nationality, country_id)
            VALUES (%s, %s, %s, %s)
        """, (full_name, passport_no, nationality, country_id))
        conn.commit()
        new_id = cursor.lastrowid
        print(f"✅ Tourist registered — ID: {new_id}")
        return new_id
    except Exception as e:
        print(f"❌ Could not register tourist: {e}")
        return None
    finally:
        cursor.close()
        conn.close()


def get_tourist_by_passport(passport_no):
    """
    Find a tourist by passport number.

    Returns:
        dict or None

    Example:
        t = get_tourist_by_passport("US123456")
        print(t["full_name"])
    """
    conn   = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM tourists WHERE passport_no = %s", (passport_no,)
    )
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row


def get_tourist_by_id(tourist_id):
    """Find a tourist by their ID number."""
    conn   = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM tourists WHERE id = %s", (tourist_id,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row


def get_all_tourists():
    """
    All tourists with country info.
    Use for the tourists table in the UI.

    Returns: list of dicts
    """
    conn   = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT
            t.id, t.full_name, t.passport_no,
            t.nationality, t.created_at,
            c.name      AS country_name,
            c.price_usd AS ticket_price
        FROM tourists t
        LEFT JOIN countries c ON t.country_id = c.id
        ORDER BY t.created_at DESC
    """)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


def search_tourists(keyword):
    """
    Search tourists by name or passport.
    Used for the search bar.

    Example:
        results = search_tourists("john")
    """
    conn   = get_connection()
    cursor = conn.cursor(dictionary=True)
    like   = f"%{keyword}%"
    cursor.execute("""
        SELECT t.*, c.name AS country_name
        FROM tourists t
        LEFT JOIN countries c ON t.country_id = c.id
        WHERE t.full_name LIKE %s OR t.passport_no LIKE %s
        ORDER BY t.created_at DESC
    """, (like, like))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


# ═══════════════════════════════════════════════
#  B. TICKET FUNCTIONS
# ═══════════════════════════════════════════════

def create_ticket(tourist_id, amount_paid, days_valid=7):
    """
    Issues a new ticket with a serial ticket number and QR code.

    What this does automatically:
        1. Gets the next serial number (TKT-2024-000001, 000002, ...)
        2. Saves the ticket to the database
        3. Generates and saves a QR code image

    Parameters:
        tourist_id  (int)   : from create_tourist()
        amount_paid (float) : in USD
        days_valid  (int)   : default 7 days

    Returns:
        dict → {"ticket_number": "TKT-2024-000001", "qr_path": "/path/to/qr.png"}
        None → on failure

    Example:
        result = create_ticket(tourist_id=1, amount_paid=50.0, days_valid=7)
        ticket_num = result["ticket_number"]
        qr_image   = result["qr_path"]
    """
    conn   = get_connection()
    cursor = conn.cursor()
    try:
        # Serial number — guaranteed unique and sequential
        ticket_number = get_next_ticket_number()

        valid_from  = datetime.date.today()
        valid_until = valid_from + datetime.timedelta(days=days_valid)

        cursor.execute("""
            INSERT INTO tickets
                (ticket_number, tourist_id, amount_paid, valid_from, valid_until)
            VALUES (%s, %s, %s, %s, %s)
        """, (ticket_number, tourist_id, amount_paid, valid_from, valid_until))
        conn.commit()

        # Generate QR code and save the path back to the ticket row
        qr_path = generate_qr(ticket_number)
        cursor.execute(
            "UPDATE tickets SET qr_path = %s WHERE ticket_number = %s",
            (qr_path, ticket_number)
        )
        conn.commit()

        print(f"✅ Ticket issued: {ticket_number}")
        return {"ticket_number": ticket_number, "qr_path": qr_path}

    except Exception as e:
        print(f"❌ Could not create ticket: {e}")
        return None
    finally:
        cursor.close()
        conn.close()


def get_ticket_by_number(ticket_number):
    """
    Full ticket + tourist info combined.
    Used at checkposts to verify.

    Returns:
        dict or None

    Example:
        t = get_ticket_by_number("TKT-2024-000001")
        print(t["full_name"], t["status"], t["valid_until"])
    """
    conn   = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT
            tk.*,
            t.full_name, t.passport_no, t.nationality
        FROM tickets tk
        JOIN tourists t ON tk.tourist_id = t.id
        WHERE tk.ticket_number = %s
    """, (ticket_number,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row


def get_all_tickets():
    """
    All tickets with tourist info.
    Used for the tickets table on the dashboard.
    """
    conn   = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT
            tk.id, tk.ticket_number, tk.amount_paid,
            tk.valid_from, tk.valid_until,
            tk.status, tk.issued_at, tk.qr_path,
            t.full_name, t.passport_no, t.nationality
        FROM tickets tk
        JOIN tourists t ON tk.tourist_id = t.id
        ORDER BY tk.issued_at DESC
    """)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


def get_tickets_by_tourist(tourist_id):
    """All tickets ever issued to one tourist."""
    conn   = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM tickets WHERE tourist_id = %s ORDER BY issued_at DESC",
        (tourist_id,)
    )
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


def cancel_ticket(ticket_number):
    """
    Cancel a ticket.

    Returns:
        True  → cancelled successfully
        False → ticket not found

    Example:
        ok = cancel_ticket("TKT-2024-000001")
    """
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE tickets SET status = 'cancelled' WHERE ticket_number = %s",
        (ticket_number,)
    )
    conn.commit()
    affected = cursor.rowcount
    cursor.close()
    conn.close()
    return affected > 0


# ═══════════════════════════════════════════════
#  C. CHECKPOST ENTRY FUNCTIONS
# ═══════════════════════════════════════════════

def record_checkpost_entry(ticket_number, checkpost_id, verified_by=""):
    """
    Records a tourist passing through a checkpost.
    Called every time staff scans a ticket at a gate.

    Checks automatically:
        ✓ Ticket exists
        ✓ Ticket is active (not cancelled)
        ✓ Ticket is not expired
        ✓ Not already checked in at this checkpost

    Parameters:
        ticket_number (str) : "TKT-2024-000001"
        checkpost_id  (int) : 1 to 6
        verified_by   (str) : staff name

    Returns:
        dict → {"success": True/False, "message": "text for UI"}

    Example:
        result = record_checkpost_entry("TKT-2024-000001", 1, "Ram Bahadur")
        if result["success"]:
            show_green()
        else:
            show_red(result["message"])
    """
    conn   = get_connection()
    cursor = conn.cursor(dictionary=True)

    # Check 1 — ticket exists?
    cursor.execute(
        "SELECT * FROM tickets WHERE ticket_number = %s", (ticket_number,)
    )
    ticket = cursor.fetchone()
    if not ticket:
        cursor.close(); conn.close()
        return {"success": False, "message": "❌ Ticket not found."}

    # Check 2 — active?
    if ticket["status"] != "active":
        cursor.close(); conn.close()
        return {"success": False, "message": f"❌ Ticket is {ticket['status']}."}

    # Check 3 — not expired?
    today = datetime.date.today()
    if today > ticket["valid_until"]:
        cursor.close(); conn.close()
        return {"success": False, "message": f"❌ Ticket expired on {ticket['valid_until']}."}

    # Check 4 — not already checked in here?
    cursor.execute("""
        SELECT id FROM checkpost_entries
        WHERE ticket_id = %s AND checkpost_id = %s
    """, (ticket["id"], checkpost_id))
    if cursor.fetchone():
        cursor.close(); conn.close()
        return {"success": False, "message": "⚠️ Already checked in at this checkpost!"}

    # All good — record it
    cursor2 = conn.cursor()
    cursor2.execute("""
        INSERT INTO checkpost_entries (ticket_id, checkpost_id, verified_by)
        VALUES (%s, %s, %s)
    """, (ticket["id"], checkpost_id, verified_by))
    conn.commit()
    cursor.close(); cursor2.close(); conn.close()
    return {"success": True, "message": "✅ Check-in recorded! Tourist may proceed."}


def get_entries_for_ticket(ticket_number):
    """
    All checkposts a tourist has passed through.
    Used to show journey progress in the UI.

    Returns: list of dicts, each has:
        checkpost_name, location, entry_time, verified_by

    Example:
        journey = get_entries_for_ticket("TKT-2024-000001")
        for stop in journey:
            print(stop["checkpost_name"], stop["entry_time"])
    """
    conn   = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT
            cp.name     AS checkpost_name,
            cp.location,
            ce.entry_time,
            ce.verified_by
        FROM checkpost_entries ce
        JOIN checkposts cp ON ce.checkpost_id = cp.id
        JOIN tickets    tk ON ce.ticket_id    = tk.id
        WHERE tk.ticket_number = %s
        ORDER BY ce.entry_time ASC
    """, (ticket_number,))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


def get_todays_entries(checkpost_id=None):
    """
    All check-ins from today.
    If checkpost_id given, filters to that gate only.
    Used for the live activity feed on the dashboard.
    """
    conn   = get_connection()
    cursor = conn.cursor(dictionary=True)
    if checkpost_id:
        cursor.execute("""
            SELECT
                ce.entry_time, ce.verified_by,
                tk.ticket_number,
                t.full_name, t.nationality,
                cp.name AS checkpost_name
            FROM checkpost_entries ce
            JOIN tickets    tk ON ce.ticket_id    = tk.id
            JOIN tourists   t  ON tk.tourist_id   = t.id
            JOIN checkposts cp ON ce.checkpost_id = cp.id
            WHERE DATE(ce.entry_time) = CURDATE()
              AND ce.checkpost_id = %s
            ORDER BY ce.entry_time DESC
        """, (checkpost_id,))
    else:
        cursor.execute("""
            SELECT
                ce.entry_time, ce.verified_by,
                tk.ticket_number,
                t.full_name, t.nationality,
                cp.name AS checkpost_name
            FROM checkpost_entries ce
            JOIN tickets    tk ON ce.ticket_id    = tk.id
            JOIN tourists   t  ON tk.tourist_id   = t.id
            JOIN checkposts cp ON ce.checkpost_id = cp.id
            WHERE DATE(ce.entry_time) = CURDATE()
            ORDER BY ce.entry_time DESC
        """)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


# ═══════════════════════════════════════════════
#  D. LOOKUP HELPERS (for UI dropdowns)
# ═══════════════════════════════════════════════

def get_all_checkposts():
    """
    All 6 checkposts.
    Your friend uses this to fill the checkpost dropdown.

    Returns: list of dicts, each has: id, name, location
    """
    conn   = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM checkposts ORDER BY id")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


def get_all_countries():
    """
    All countries with prices.
    Your friend uses this for the nationality dropdown.
    When a country is selected, show its price_usd as the default fee.

    Returns: list of dicts, each has: id, name, price_usd
    """
    conn   = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM countries ORDER BY name")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


def get_country_price(country_id):
    """
    Price for one specific country.
    Call this to auto-fill the amount field when nationality is chosen.

    Example:
        price = get_country_price(3)  # → 50.0 for USA
    """
    conn   = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT price_usd FROM countries WHERE id = %s", (country_id,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return float(row["price_usd"]) if row else 0.0


# ═══════════════════════════════════════════════
#  E. DASHBOARD STATS
# ═══════════════════════════════════════════════

def get_dashboard_stats():
    """
    All key numbers for the dashboard — one call gets everything.

    Your friend calls this on page load:
        stats = get_dashboard_stats()
        show_card("Tickets Today",  stats["tickets_today"])
        show_card("Revenue Today",  stats["revenue_today"])
        show_card("Active Tickets", stats["active_tickets"])
        show_card("Total Tourists", stats["total_tourists"])
        show_card("Check-ins Today",stats["checkins_today"])

    Returns: dict
    """
    conn   = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT COUNT(*) FROM tickets WHERE DATE(issued_at) = CURDATE()"
    )
    tickets_today = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COALESCE(SUM(amount_paid), 0) FROM tickets WHERE DATE(issued_at) = CURDATE()"
    )
    revenue_today = float(cursor.fetchone()[0])

    cursor.execute("SELECT COUNT(*) FROM tickets WHERE status = 'active'")
    active_tickets = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM tourists")
    total_tourists = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM checkpost_entries WHERE DATE(entry_time) = CURDATE()"
    )
    checkins_today = cursor.fetchone()[0]

    cursor.close()
    conn.close()

    return {
        "tickets_today":  tickets_today,
        "revenue_today":  round(revenue_today, 2),
        "active_tickets": active_tickets,
        "total_tourists": total_tourists,
        "checkins_today": checkins_today,
    }