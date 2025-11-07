"""
Test Supabase connection and basic operations
"""

from src.supabase_db import SupabaseDB
import sys


def test_connection():
    """Test Supabase connection."""
    print("\n" + "="*60)
    print("Testing Supabase Connection")
    print("="*60)
    
    try:
        # Initialize connection
        print("\n1. Connecting to Supabase...")
        db = SupabaseDB()
        print("   ✓ Connected successfully!")
        
        # Test getting websites
        print("\n2. Testing database read...")
        websites = db.client.table('websites').select('*').execute()
        print(f"   ✓ Found {len(websites.data)} websites")
        for website in websites.data:
            print(f"      - {website['name']} ({website['validity_hours']}h validity)")
        
        # Test getting accounts
        print("\n3. Testing accounts query...")
        accounts = db.client.table('accounts').select('id, username, status, websites(name)').execute()
        print(f"   ✓ Found {len(accounts.data)} accounts")
        for account in accounts.data[:5]:  # Show first 5
            print(f"      - {account['username']} ({account['websites']['name']}) - {account['status']}")
        
        # Test available accounts function
        print("\n4. Testing available accounts...")
        available = db.get_available_accounts('unlocktool')
        print(f"   ✓ Found {len(available)} available accounts for unlocktool")
        
        # Test statistics
        print("\n5. Testing statistics...")
        stats = db.get_dashboard_stats()
        print(f"   ✓ Total Accounts: {stats['total_accounts']}")
        print(f"   ✓ Available: {stats['available_accounts']}")
        print(f"   ✓ Rented: {stats['rented_accounts']}")
        print(f"   ✓ Exceptions: {stats['exception_accounts']}")
        
        print("\n" + "="*60)
        print("✓ All tests passed! Supabase is ready to use!")
        print("="*60)
        
        return True
        
    except FileNotFoundError:
        print("\n✗ Error: config/supabase_config.json not found!")
        print("\nPlease create the config file with your Supabase credentials:")
        print("1. Go to https://supabase.com/dashboard")
        print("2. Select your project")
        print("3. Go to Project Settings → API")
        print("4. Copy URL and service_role key")
        print("5. Update config/supabase_config.json")
        return False
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        print("\nMake sure:")
        print("1. You've created a Supabase project")
        print("2. You've run the SQL schema (supabase_schema.sql)")
        print("3. Your credentials in config/supabase_config.json are correct")
        return False


if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)
