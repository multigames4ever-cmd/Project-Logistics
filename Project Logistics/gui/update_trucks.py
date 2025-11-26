"""
Update Trucks Window
Allows updating truck details and status.
"""
import mysql.connector

conn = mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    password="",
    database="inventories"
)

cursor = conn.cursor()

# Update trucks with default values
cursor.execute("""
    UPDATE trucks 
    SET license_plate = CONCAT('LIC-', id),
        model = CONCAT('Model ', id),
        capacity = 1000.00
    WHERE license_plate IS NULL
""")

conn.commit()
print(f"Updated {cursor.rowcount} trucks with default values")

# Show current trucks
cursor.execute("SELECT id, license_plate, model, capacity, status FROM trucks")
print("\nCurrent trucks:")
for truck in cursor.fetchall():
    print(truck)

conn.close()
