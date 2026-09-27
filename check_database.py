import sqlite3
import os

database_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "hospital.db"
)

conn = sqlite3.connect(database_path)

conn.execute("""
    CREATE TABLE IF NOT EXISTS patients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        age INTEGER NOT NULL,
        gender TEXT NOT NULL,
        phone TEXT NOT NULL,
        disease TEXT NOT NULL
    )
""")

conn.execute("""
    CREATE TABLE IF NOT EXISTS doctors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        specialization TEXT NOT NULL,
        department TEXT
    )
""")

conn.execute("""
    CREATE TABLE IF NOT EXISTS beds (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        bed_number TEXT NOT NULL UNIQUE,
        ward TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'Available'
    )
""")

doctor_count = conn.execute(
    "SELECT COUNT(*) FROM doctors"
).fetchone()[0]

if doctor_count == 0:
    conn.executemany("""
        INSERT INTO doctors
        (name, specialization, department)
        VALUES (?, ?, ?)
    """, [
        ("Dr. Rahul Sharma", "Cardiologist", "Cardiology"),
        ("Dr. Priya Patil", "Neurologist", "Neurology"),
        ("Dr. Amit Verma", "General Physician", "General Medicine")
    ])

bed_count = conn.execute(
    "SELECT COUNT(*) FROM beds"
).fetchone()[0]

if bed_count == 0:
    conn.executemany("""
        INSERT INTO beds
        (bed_number, ward, status)
        VALUES (?, ?, ?)
    """, [
        ("B-101", "General Ward", "Available"),
        ("B-102", "General Ward", "Occupied"),
        ("B-103", "General Ward", "Available"),
        ("B-104", "ICU", "Occupied"),
        ("B-105", "ICU", "Available"),
        ("B-106", "Private Ward", "Available")
    ])

conn.commit()

print("Database created successfully!")
print("Database location:", database_path)

print("\nTables available:")
tables = conn.execute("""
    SELECT name
    FROM sqlite_master
    WHERE type='table'
""").fetchall()

for table in tables:
    print("-", table[0])

conn.close()
