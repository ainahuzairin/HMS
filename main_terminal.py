import sqlite3
import hashlib
import os
from datetime import date, timedelta

DB_NAME = "hostel.db"

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header(title):
    clear()
    print("=" * 50)
    print(f"   HOSTEL MANAGEMENT SYSTEM (HMS)")
    print(f"   {title}")
    print("=" * 50)

def login():
    clear()
    print("=" * 50)
    print("   *** HOSTEL MANAGEMENT SYSTEM (HMS) ***")
    print("=" * 50)
    email = input("\nUsername: ")
    password = input("Password: ")
    pw_hash = hashlib.sha256(password.encode()).hexdigest()
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT admin_id, full_name FROM admin WHERE email=? AND password_hash=?", (email, pw_hash))
    result = cursor.fetchone()
    conn.close()
    return result

def main_menu():
    print_header("MAIN MENU")
    print("\n  [1] Student Registration")
    print("  [2] Room Allocation")
    print("  [3] Fines Management")
    print("  [4] Complaints & Maintenance")
    print("  [5] Reports")
    print("  [0] Logout")
    print("\n" + "=" * 50)
    return input("  Select option: ").strip()

# ─── STUDENT MODULE ───────────────────────────────
def student_menu():
    while True:
        print_header("STUDENT REGISTRATION")
        print("\n  [1] Add Student")
        print("  [2] View All Students")
        print("  [3] Update Student")
        print("  [4] Delete Student")
        print("  [0] Back")
        print("=" * 50)
        choice = input("  Select option: ").strip()

        if choice == "1":
            add_student()
        elif choice == "2":
            view_students()
        elif choice == "3":
            update_student()
        elif choice == "4":
            delete_student()
        elif choice == "0":
            break

def add_student():
    print_header("ADD STUDENT")
    name = input("Full Name      : ").strip()
    ic   = input("IC Number      : ").strip()
    if not name or not ic:
        print("\n[!] Name and IC Number are required!")
        input("\nPress Enter to continue...")
        return
    phone     = input("Phone          : ").strip()
    email     = input("Email          : ").strip()
    emergency = input("Emergency Contact: ").strip()
    medical   = input("Medical Notes  : ").strip()
    try:
        conn = sqlite3.connect(DB_NAME)
        conn.execute("""INSERT INTO student (full_name, ic_number, phone, email, emergency_contact, medical_notes)
                        VALUES (?,?,?,?,?,?)""", (name, ic, phone, email, emergency, medical))
        conn.commit()
        conn.close()
        print("\n[✓] Student added successfully!")
    except sqlite3.IntegrityError:
        print("\n[!] IC Number already exists!")
    input("\nPress Enter to continue...")

def view_students():
    print_header("ALL STUDENTS")
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT student_id, full_name, ic_number, phone, status FROM student")
    rows = cursor.fetchall()
    conn.close()
    if not rows:
        print("\n  No students found.")
    else:
        print(f"\n  {'ID':<5} {'Name':<25} {'IC Number':<15} {'Phone':<15} {'Status'}")
        print("  " + "-" * 70)
        for row in rows:
            print(f"  {row[0]:<5} {row[1]:<25} {row[2]:<15} {str(row[3]):<15} {row[4]}")
    input("\nPress Enter to continue...")

def update_student():
    print_header("UPDATE STUDENT")
    view_students()
    sid = input("Enter Student ID to update: ").strip()
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM student WHERE student_id=?", (sid,))
    row = cursor.fetchone()
    if not row:
        print("[!] Student not found!")
        conn.close()
        input("\nPress Enter to continue...")
        return
    print(f"\nLeave blank to keep current value")
    name      = input(f"Full Name [{row[1]}]: ").strip() or row[1]
    ic        = input(f"IC Number [{row[2]}]: ").strip() or row[2]
    phone     = input(f"Phone [{row[3]}]: ").strip() or row[3]
    email     = input(f"Email [{row[4]}]: ").strip() or row[4]
    emergency = input(f"Emergency [{row[5]}]: ").strip() or row[5]
    medical   = input(f"Medical [{row[6]}]: ").strip() or row[6]
    conn.execute("""UPDATE student SET full_name=?, ic_number=?, phone=?, email=?,
                    emergency_contact=?, medical_notes=? WHERE student_id=?""",
                 (name, ic, phone, email, emergency, medical, sid))
    conn.commit()
    conn.close()
    print("\n[✓] Student updated!")
    input("\nPress Enter to continue...")

def delete_student():
    print_header("DELETE STUDENT")
    view_students()
    sid = input("Enter Student ID to delete: ").strip()
    confirm = input(f"Are you sure? (yes/no): ").strip().lower()
    if confirm == "yes":
        conn = sqlite3.connect(DB_NAME)
        conn.execute("DELETE FROM student WHERE student_id=?", (sid,))
        conn.commit()
        conn.close()
        print("\n[✓] Student deleted!")
    input("\nPress Enter to continue...")

    # part marsya
    # part miera
    # part aliah

# ─── REPORTS MODULE ───────────────────────────────
def show_reports():
    print_header("REPORTS & SUMMARY")
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    stats = [
        ("Total Students",  "SELECT COUNT(*) FROM student WHERE status='active'"),
        ("Total Rooms",     "SELECT COUNT(*) FROM room"),
        ("Available Rooms", "SELECT COUNT(*) FROM room WHERE status='available'"),
        ("Full Rooms",      "SELECT COUNT(*) FROM room WHERE status='full'"),
        ("Unpaid Fines",    "SELECT COUNT(*) FROM fine WHERE payment_status='unpaid'"),
        ("Open Complaints", "SELECT COUNT(*) FROM complaint WHERE status='open'"),
    ]

    print("\n  --- SYSTEM SUMMARY ---\n")
    for label, query in stats:
        cursor.execute(query)
        count = cursor.fetchone()[0]
        print(f"  {label:<25}: {count}")

    print("\n  --- RECENT UNPAID FINES ---\n")
    cursor.execute("""SELECT fine_id, student_id, violation_type, amount, due_date
                      FROM fine WHERE payment_status='unpaid' ORDER BY due_date LIMIT 5""")
    rows = cursor.fetchall()
    if rows:
        print(f"  {'ID':<5} {'St.ID':<7} {'Violation':<25} {'RM':<8} {'Due'}")
        print("  " + "-" * 55)
        for r in rows:
            print(f"  {r[0]:<5} {r[1]:<7} {r[2]:<25} {r[3]:<8} {r[4]}")
    else:
        print("  No unpaid fines.")

    conn.close()
    input("\nPress Enter to continue...")


# ─── MAIN ─────────────────────────────────────────
def main():
    from database import initialize_db
    initialize_db()

    result = login()
    if not result:
        print("\n[!] Invalid credentials. Exiting.")
        return

    admin_id, full_name = result
    print(f"\n[✓] Welcome, {full_name}!")

    while True:
        choice = main_menu()
        if choice == "1":
            student_menu()
        elif choice == "2":
            room_menu()
        elif choice == "3":
            fines_menu(admin_id)
        elif choice == "4":
            complaint_menu(admin_id)
        elif choice == "5":
            show_reports()
        elif choice == "0":
            clear()
            print("  Goodbye! System logged out.")
            break

if __name__ == "__main__":
    main()