import sqlite3
import os

DB_NAME = "hostel.db"

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def initialize_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS admin (
            admin_id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            role TEXT DEFAULT 'warden',
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS student (
            student_id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            ic_number TEXT UNIQUE NOT NULL,
            phone TEXT,
            email TEXT,
            emergency_contact TEXT,
            medical_notes TEXT,
            check_in_date DATE DEFAULT CURRENT_DATE,
            status TEXT DEFAULT 'active'
        );
        CREATE TABLE IF NOT EXISTS room (
            room_id INTEGER PRIMARY KEY AUTOINCREMENT,
            room_number TEXT UNIQUE NOT NULL,
            block TEXT,
            floor INTEGER,
            capacity INTEGER DEFAULT 4,
            current_occupancy INTEGER DEFAULT 0,
            status TEXT DEFAULT 'available'
        );
        CREATE TABLE IF NOT EXISTS room_allocation (
            allocation_id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER REFERENCES student(student_id),
            room_id INTEGER REFERENCES room(room_id),
            bed_number INTEGER,
            allocated_date DATE DEFAULT CURRENT_DATE,
            vacated_date DATE,
            status TEXT DEFAULT 'active'
        );
        CREATE TABLE IF NOT EXISTS fine (
            fine_id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER REFERENCES student(student_id),
            admin_id INTEGER REFERENCES admin(admin_id),
            violation_type TEXT NOT NULL,
            amount REAL DEFAULT 0.0,
            issued_date DATE DEFAULT CURRENT_DATE,
            due_date DATE,
            payment_status TEXT DEFAULT 'unpaid',
            notes TEXT
        );
        CREATE TABLE IF NOT EXISTS complaint (
            complaint_id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER REFERENCES student(student_id),
            admin_id INTEGER REFERENCES admin(admin_id),
            staff_id INTEGER,
            category TEXT,
            description TEXT,
            status TEXT DEFAULT 'open',
            submitted_date DATE DEFAULT CURRENT_DATE,
            resolved_date DATE
        );
        CREATE TABLE IF NOT EXISTS maintenance_staff (
            staff_id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            specialization TEXT,
            phone TEXT,
            status TEXT DEFAULT 'available'
        );
    """)
    cursor.execute("SELECT COUNT(*) FROM admin")
    if cursor.fetchone()[0] == 0:
        import hashlib
        pw = hashlib.sha256("admin123".encode()).hexdigest()
        cursor.execute(
            "INSERT INTO admin (full_name, email, password_hash, role) VALUES (?, ?, ?, ?)",
            ("Administrator", "admin@hostel.com", pw, "admin")
        )
    conn.commit()
    conn.close()
    print("Database initialized.")

if __name__ == "__main__":
    initialize_db()