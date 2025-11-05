from src.database import PasswordResetDB

db = PasswordResetDB()

print("\n=== Password History for Account 1 (vpbgkt) ===")
history = db.get_password_history(1, 10)
for i, h in enumerate(history, 1):
    print(f"{i}. {h['reset_date']} | Status: {h['status']} | Message: {h.get('message', 'N/A')}")

print("\n=== Account Details ===")
import sqlite3
conn = sqlite3.connect(db.db_path)
cursor = conn.cursor()
cursor.execute("""
    SELECT username, status, last_reset, failed_login_attempts, exception_reason 
    FROM accounts WHERE id = 1
""")
account = cursor.fetchone()
conn.close()

print(f"Username: {account[0]}")
print(f"Status: {account[1]}")
print(f"Last Reset: {account[2]}")
print(f"Failed Login Attempts: {account[3]}")
print(f"Exception Reason: {account[4]}")

print("\n✓ Database verification complete!")
