"""
Script to add new accounts directly to the database.
Run this to manually add accounts without modifying config file.
"""

from src.database import PasswordResetDB

def add_account():
    db = PasswordResetDB()
    
    print("\n=== Add New Account to Database ===\n")
    
    # Get account details from user
    website = input("Website name (e.g., unlocktool, androidmultitool): ").strip()
    username = input("Username: ").strip()
    password = input("Current password: ").strip()
    email = input("Email (optional, press Enter to skip): ").strip() or None
    
    # Verify website exists
    website_info = db.get_website(website)
    if not website_info:
        print(f"\n❌ Error: Website '{website}' not found in database!")
        print("\nAvailable websites:")
        import sqlite3
        conn = sqlite3.connect(db.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name, validity_hours FROM websites")
        for row in cursor.fetchall():
            print(f"  - {row[0]} (Valid for {row[1]} hours)")
        conn.close()
        return
    
    # Add account to database
    try:
        account_id = db.add_account(website, username, password, email)
        print(f"\n✓ Account added successfully!")
        print(f"  ID: {account_id}")
        print(f"  Website: {website}")
        print(f"  Username: {username}")
        print(f"  Email: {email or 'N/A'}")
        
        # Show how to add to config
        print("\n📝 To enable automated password reset for this account,")
        print("   add the following to config/accounts.json:")
        print("\n" + "="*60)
        print(f'''    {{
      "id": {account_id},
      "website": "{website}",
      "username": "{username}",
      "current_password": "{password}",
      "email": "{email or 'N/A'}",
      "enabled": true
    }}''')
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Error adding account: {e}")

if __name__ == "__main__":
    add_account()
