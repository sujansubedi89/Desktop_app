# database/sync.py
#
# Syncs offline data to the cloud when internet is available.
# Call sync_all() when your app detects internet connectivity.

from database.connection import get_connection
import datetime


def get_unsynced_tickets():
    """All tickets not yet sent to cloud."""
    conn   = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT tk.*, t.full_name, t.passport_no, t.nationality
        FROM tickets tk
        JOIN tourists t ON tk.tourist_id = t.id
        WHERE tk.synced = 0
    """)
    rows = cursor.fetchall()
    cursor.close(); conn.close()
    return rows


def get_unsynced_entries():
    """All checkpost entries not yet sent to cloud."""
    conn   = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT ce.*, tk.ticket_number, cp.name AS checkpost_name
        FROM checkpost_entries ce
        JOIN tickets    tk ON ce.ticket_id    = tk.id
        JOIN checkposts cp ON ce.checkpost_id = cp.id
        WHERE ce.synced = 0
    """)
    rows = cursor.fetchall()
    cursor.close(); conn.close()
    return rows


def mark_tickets_synced(ticket_ids):
    if not ticket_ids:
        return
    conn   = get_connection()
    cursor = conn.cursor()
    placeholders = ",".join(["%s"] * len(ticket_ids))
    cursor.execute(
        f"UPDATE tickets SET synced = 1 WHERE id IN ({placeholders})",
        ticket_ids
    )
    conn.commit()
    cursor.close(); conn.close()


def mark_entries_synced(entry_ids):
    if not entry_ids:
        return
    conn   = get_connection()
    cursor = conn.cursor()
    placeholders = ",".join(["%s"] * len(entry_ids))
    cursor.execute(
        f"UPDATE checkpost_entries SET synced = 1 WHERE id IN ({placeholders})",
        entry_ids
    )
    conn.commit()
    cursor.close(); conn.close()


def sync_all():
    """
    Call this when internet is detected.
    Replace the TODO block with your real cloud API later.
    """
    tickets = get_unsynced_tickets()
    entries = get_unsynced_entries()
    print(f"📡 Syncing {len(tickets)} tickets, {len(entries)} entries...")

    # ── TODO: replace with your cloud API ───────────────────
    # import requests
    # r = requests.post("https://your-api.com/sync", json={
    #     "tickets": tickets, "entries": entries
    # })
    # if r.status_code != 200:
    #     print("❌ Sync failed!"); return None
    # ─────────────────────────────────────────────────────────

    if tickets:
        mark_tickets_synced([t["id"] for t in tickets])
    if entries:
        mark_entries_synced([e["id"] for e in entries])

    result = {
        "tickets_synced": len(tickets),
        "entries_synced": len(entries),
        "synced_at":      datetime.datetime.now().isoformat(),
    }
    print(f"✅ Sync done: {result}")
    return result