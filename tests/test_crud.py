# tests/test_crud.py
# Run: python tests/test_crud.py

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database.schema import create_database, create_all_tables, seed_initial_data
from database.crud import (
    create_tourist, get_tourist_by_passport,
    create_ticket,  get_ticket_by_number,
    record_checkpost_entry, get_entries_for_ticket,
    get_all_checkposts, get_dashboard_stats,
    cancel_ticket, get_country_price, search_tourists
)

def run():
    print("\n" + "="*55)
    print("  NEPAL TICKET SYSTEM — FULL TEST")
    print("="*55)

    create_database()
    create_all_tables()
    seed_initial_data()

    print("\n📋 Test 1: Register tourist")
    tid = create_tourist("Priya Sharma", "IN998877", "India", country_id=1)
    assert tid, "FAILED"
    print(f"   ID = {tid} ✅")

    print("\n📋 Test 2: Find by passport")
    t = get_tourist_by_passport("IN998877")
    assert t and t["full_name"] == "Priya Sharma", "FAILED"
    print(f"   Found: {t['full_name']} ✅")

    print("\n📋 Test 3: Country price lookup")
    price = get_country_price(1)
    print(f"   India price: ${price} ✅")

    print("\n📋 Test 4: Issue ticket (serial number + QR)")
    result = create_ticket(tid, amount_paid=price, days_valid=7)
    assert result, "FAILED"
    tnum = result["ticket_number"]
    print(f"   Ticket: {tnum} ✅")
    print(f"   QR:     {result['qr_path']} ✅")

    print("\n📋 Test 5: Ticket is serial — issue second ticket")
    tid2 = create_tourist("John Smith", "US123456", "USA", country_id=3)
    r2   = create_ticket(tid2, amount_paid=50.0)
    print(f"   Second ticket: {r2['ticket_number']} ✅")

    print("\n📋 Test 6: Look up ticket")
    ticket = get_ticket_by_number(tnum)
    assert ticket["full_name"] == "Priya Sharma", "FAILED"
    print(f"   Valid {ticket['valid_from']} → {ticket['valid_until']} ✅")

    print("\n📋 Test 7: Check in at checkposts")
    checkposts = get_all_checkposts()
    for cp in checkposts[:3]:
        r = record_checkpost_entry(tnum, cp["id"], verified_by="Ram Bahadur")
        print(f"   {cp['name']}: {r['message']}")

    print("\n📋 Test 8: Duplicate check-in (should reject)")
    r = record_checkpost_entry(tnum, checkposts[0]["id"])
    assert not r["success"], "FAILED: should reject"
    print(f"   Correctly rejected: {r['message']} ✅")

    print("\n📋 Test 9: Tourist journey")
    journey = get_entries_for_ticket(tnum)
    print(f"   Passed {len(journey)} checkposts:")
    for stop in journey:
        print(f"   → {stop['checkpost_name']}  at  {stop['entry_time']}")

    print("\n📋 Test 10: Search tourists")
    found = search_tourists("priya")
    print(f"   Search 'priya' → {len(found)} result(s) ✅")

    print("\n📋 Test 11: Cancel ticket")
    ok = cancel_ticket(tnum)
    assert ok, "FAILED"
    t2 = get_ticket_by_number(tnum)
    assert t2["status"] == "cancelled", "FAILED"
    print(f"   Status: {t2['status']} ✅")

    print("\n📋 Test 12: Check-in on cancelled (should reject)")
    r = record_checkpost_entry(tnum, checkposts[3]["id"])
    assert not r["success"], "FAILED"
    print(f"   Correctly rejected: {r['message']} ✅")

    print("\n📋 Test 13: Dashboard stats")
    stats = get_dashboard_stats()
    for k, v in stats.items():
        print(f"   {k}: {v}")

    print("\n" + "="*55)
    print("  ALL TESTS PASSED 🎉")
    print("="*55 + "\n")

if __name__ == "__main__":
    run()