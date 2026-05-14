# database/schema.py
#
# Run this file ONCE to set up the entire database.
# Safe to run again — IF NOT EXISTS means nothing gets deleted.
#
# Tables created:
#   1. ticket_counter   ← tracks the serial number
#   2. countries        ← country names + prices
#   3. checkposts       ← the 6 physical gates
#   4. tourists         ← one row per tourist
#   5. tickets          ← one row per ticket issued
#   6. checkpost_entries← one row per checkpost scan

from database.connection import get_connection_no_db, get_connection


def create_database():
    """Step 1: Create the MySQL database itself."""
    conn   = get_connection_no_db()
    cursor = conn.cursor()
    cursor.execute(
        "CREATE DATABASE IF NOT EXISTS nepal_tickets "
        "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
    )
    print("✅ Database 'nepal_tickets' ready")
    cursor.close()
    conn.close()


def create_all_tables():
    """Step 2: Create all 6 tables."""
    conn   = get_connection()
    cursor = conn.cursor()

    # ── 1. ticket_counter ────────────────────────────────────────────────
    # Stores the current serial number per year.
    # e.g. year=2024, counter_value=42 means 42 tickets issued this year.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ticket_counter (
            year          INT  NOT NULL PRIMARY KEY,
            counter_value INT  NOT NULL DEFAULT 0
        )
    """)

    # ── 2. countries ─────────────────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS countries (
            id        INT           AUTO_INCREMENT PRIMARY KEY,
            name      VARCHAR(100)  NOT NULL UNIQUE,
            price_usd DECIMAL(10,2) NOT NULL DEFAULT 0.00
        )
    """)

    # ── 3. checkposts ────────────────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS checkposts (
            id       INT          AUTO_INCREMENT PRIMARY KEY,
            name     VARCHAR(150) NOT NULL UNIQUE,
            location VARCHAR(200)
        )
    """)

    # ── 4. tourists ──────────────────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tourists (
            id          INT          AUTO_INCREMENT PRIMARY KEY,
            full_name   VARCHAR(200) NOT NULL,
            passport_no VARCHAR(50)  NOT NULL UNIQUE,
            nationality VARCHAR(100) NOT NULL,
            country_id  INT,
            created_at  DATETIME     DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (country_id) REFERENCES countries(id)
        )
    """)

    # ── 5. tickets ───────────────────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            id            INT           AUTO_INCREMENT PRIMARY KEY,
            ticket_number VARCHAR(30)   NOT NULL UNIQUE,
            tourist_id    INT           NOT NULL,
            amount_paid   DECIMAL(10,2) NOT NULL,
            valid_from    DATE          NOT NULL,
            valid_until   DATE          NOT NULL,
            status        VARCHAR(20)   DEFAULT 'active',
            qr_path       VARCHAR(500),
            issued_at     DATETIME      DEFAULT CURRENT_TIMESTAMP,
            synced        TINYINT(1)    DEFAULT 0,
            FOREIGN KEY (tourist_id) REFERENCES tourists(id)
        )
    """)

    # ── 6. checkpost_entries ─────────────────────────────────────────────
    # UNIQUE KEY (ticket_id, checkpost_id) prevents double check-in
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS checkpost_entries (
            id           INT          AUTO_INCREMENT PRIMARY KEY,
            ticket_id    INT          NOT NULL,
            checkpost_id INT          NOT NULL,
            entry_time   DATETIME     DEFAULT CURRENT_TIMESTAMP,
            verified_by  VARCHAR(100),
            synced       TINYINT(1)   DEFAULT 0,
            FOREIGN KEY (ticket_id)    REFERENCES tickets(id),
            FOREIGN KEY (checkpost_id) REFERENCES checkposts(id),
            UNIQUE KEY no_double_checkin (ticket_id, checkpost_id)
        )
    """)

    conn.commit()
    cursor.close()
    conn.close()
    print("✅ All 6 tables created!")


def seed_initial_data():
    """Step 3: Add starter data. Safe to run again — uses INSERT IGNORE."""
    conn   = get_connection()
    cursor = conn.cursor()

    checkposts = [
        ("Birgunj Entry Gate",     "Province 2 - Madhesh"),
        ("Kakarvitta Checkpoint",  "Province 1 - Koshi"),
        ("Bhairahawa Border",      "Lumbini Province"),
        ("Nepalgunj Gate",         "Karnali Province"),
        ("Mahendranagar Post",     "Sudurpashchim Province"),
        ("Rasuwagadhi Checkpoint", "Bagmati Province"),
    ]
    cursor.executemany(
        "INSERT IGNORE INTO checkposts (name, location) VALUES (%s, %s)",
        checkposts
    )

    countries = [
        ("India",          15.00),
        ("China",          25.00),
        ("USA",            50.00),
        ("United Kingdom", 50.00),
        ("Germany",        50.00),
        ("Australia",      50.00),
        ("Japan",          40.00),
        ("France",         50.00),
        ("Canada",         50.00),
        ("South Korea",    40.00),
        ("Other",          30.00),
    ]
    cursor.executemany(
        "INSERT IGNORE INTO countries (name, price_usd) VALUES (%s, %s)",
        countries
    )

    conn.commit()
    cursor.close()
    conn.close()
    print("✅ Starter data added!")


if __name__ == "__main__":
    create_database()
    create_all_tables()
    seed_initial_data()
    print("\n🎉 Full database setup complete!")