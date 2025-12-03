import sqlite3

DB_PATH = "securemed.db"

def create_audit_trail_table():
    # make activity log table for tracking everything
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""CREATE TABLE IF NOT EXISTS activity_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        username TEXT NOT NULL,
        action_type TEXT NOT NULL,
        description TEXT NOT NULL,
        details TEXT,
        ip_address TEXT
    )""")

    conn.commit()
    conn.close()
    print("Activity log table created successfully!")

if __name__ == "__main__":
    create_audit_trail_table()
