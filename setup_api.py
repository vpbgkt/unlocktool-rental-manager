"""
Test script to create an API key and demonstrate usage
"""

from src.api_manager import APIManager
from src.database import PasswordResetDB

def main():
    print("\n" + "="*60)
    print("Setting up API Management System")
    print("="*60)
    
    api_manager = APIManager()
    db = PasswordResetDB()
    
    # Initialize API tables
    print("\n✓ Initializing API tables...")
    api_manager._init_api_tables()
    
    # Create a demo API key
    print("\n✓ Creating demo API key...")
    result = api_manager.generate_api_key(
        name="Demo Customer Portal",
        email="demo@example.com",
        rate_limit=100,
        notes="Demo API key for testing"
    )
    
    print("\n" + "="*60)
    print("Demo API Key Created Successfully!")
    print("="*60)
    print(f"\nAPI Key ID: {result['id']}")
    print(f"Name: {result['name']}")
    print(f"Email: {result['email']}")
    print(f"Rate Limit: {result['rate_limit']} requests/day")
    print(f"Status: {result['status']}")
    print("\n" + "="*60)
    print("🔑 API KEY (save this):")
    print("="*60)
    print(f"\n{result['api_key']}\n")
    print("="*60)
    
    # Show current system status
    print("\n✓ Checking system status...")
    
    import sqlite3
    conn = sqlite3.connect(db.db_path)
    cursor = conn.cursor()
    
    # Count available accounts
    cursor.execute("SELECT COUNT(*) FROM accounts WHERE status = 'available'")
    available_count = cursor.fetchone()[0]
    
    # Count websites
    cursor.execute("SELECT name, validity_hours FROM websites")
    websites = cursor.fetchall()
    
    conn.close()
    
    print(f"\n📊 System Status:")
    print(f"   Available Accounts: {available_count}")
    print(f"   Websites:")
    for website in websites:
        print(f"      - {website[0]} (Valid for {website[1]} hours)")
    
    print("\n" + "="*60)
    print("Next Steps:")
    print("="*60)
    print("\n1. Start the API server:")
    print("   .\\venv\\Scripts\\python.exe api_server.py")
    print("\n2. Test the API with curl:")
    print(f"   curl -H \"X-API-Key: {result['api_key']}\" http://localhost:5000/api/accounts/available")
    print("\n3. Rent an account:")
    print(f"   curl -X POST -H \"X-API-Key: {result['api_key']}\" -H \"Content-Type: application/json\" -d '{{\"website\":\"unlocktool\"}}' http://localhost:5000/api/accounts/rent")
    print("\n4. View your statistics:")
    print(f"   curl -H \"X-API-Key: {result['api_key']}\" http://localhost:5000/api/stats/me")
    print("\n5. Manage API keys:")
    print("   .\\venv\\Scripts\\python.exe manage_api_keys.py")
    print("\n" + "="*60)

if __name__ == "__main__":
    main()
