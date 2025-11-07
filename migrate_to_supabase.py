"""
Migrate data from local SQLite to Supabase
"""

import sqlite3
from src.supabase_db import SupabaseDB
from datetime import datetime


def migrate_to_supabase():
    """Migrate all data from SQLite to Supabase."""
    print("\n" + "="*60)
    print("Migrating Data: SQLite → Supabase")
    print("="*60)
    
    try:
        # Connect to Supabase
        print("\n1. Connecting to Supabase...")
        supabase_db = SupabaseDB()
        print("   ✓ Connected to Supabase")
        
        # Connect to local SQLite
        print("\n2. Reading local SQLite database...")
        local_conn = sqlite3.connect("database/rental_system.db")
        local_cursor = local_conn.cursor()
        print("   ✓ Connected to local database")
        
        # Migrate websites (already exist in Supabase schema)
        print("\n3. Verifying websites...")
        local_cursor.execute("SELECT name, url, validity_hours, description FROM websites")
        websites = local_cursor.fetchall()
        print(f"   ✓ Found {len(websites)} websites in local database")
        
        # Migrate accounts
        print("\n4. Migrating accounts...")
        local_cursor.execute("""
            SELECT a.id, w.name, a.username, a.email, a.current_password, 
                   a.status, a.last_reset, a.failed_login_attempts, 
                   a.last_failed_login, a.exception_reason
            FROM accounts a
            JOIN websites w ON a.website_id = w.id
        """)
        accounts = local_cursor.fetchall()
        
        account_map = {}  # Map old IDs to new IDs
        success_count = 0
        
        for account in accounts:
            old_id, website, username, email, password, status, last_reset, \
                failed_attempts, last_failed, exception_reason = account
            
            try:
                # Add account to Supabase
                new_id = supabase_db.add_account(
                    website_name=website,
                    username=username,
                    password=password,
                    email=email
                )
                
                # Update status if not available
                if status != 'available':
                    supabase_db.client.table('accounts').update({
                        'status': status,
                        'last_reset': last_reset,
                        'failed_login_attempts': failed_attempts or 0,
                        'last_failed_login': last_failed,
                        'exception_reason': exception_reason
                    }).eq('id', new_id).execute()
                
                account_map[old_id] = new_id
                success_count += 1
                print(f"   ✓ Migrated: {username} ({website})")
                
            except Exception as e:
                print(f"   ✗ Failed to migrate {username}: {e}")
        
        print(f"\n   ✓ Migrated {success_count}/{len(accounts)} accounts")
        
        # Migrate password history
        print("\n5. Migrating password history...")
        local_cursor.execute("""
            SELECT account_id, old_password, new_password, reset_date, status, message
            FROM password_history
            ORDER BY reset_date ASC
        """)
        history = local_cursor.fetchall()
        
        history_count = 0
        for record in history:
            old_account_id, old_pwd, new_pwd, reset_date, status, message = record
            
            if old_account_id in account_map:
                new_account_id = account_map[old_account_id]
                
                try:
                    supabase_db.client.table('password_history').insert({
                        'account_id': new_account_id,
                        'old_password': old_pwd,
                        'new_password': new_pwd,
                        'reset_date': reset_date,
                        'status': status,
                        'message': message
                    }).execute()
                    
                    history_count += 1
                    
                except Exception as e:
                    print(f"   ✗ Failed to migrate history record: {e}")
        
        print(f"   ✓ Migrated {history_count}/{len(history)} password history records")
        
        # Close local connection
        local_conn.close()
        
        # Verify migration
        print("\n6. Verifying migration...")
        stats = supabase_db.get_dashboard_stats()
        print(f"   ✓ Total accounts in Supabase: {stats['total_accounts']}")
        print(f"   ✓ Available: {stats['available_accounts']}")
        print(f"   ✓ Rented: {stats['rented_accounts']}")
        print(f"   ✓ Exceptions: {stats['exception_accounts']}")
        
        print("\n" + "="*60)
        print("✓ Migration Complete!")
        print("="*60)
        print("\nYour data is now in Supabase:")
        print(f"  - {success_count} accounts migrated")
        print(f"  - {history_count} password history records migrated")
        print(f"  - {len(websites)} websites configured")
        print("\nYou can now:")
        print("  1. View data in Supabase Dashboard")
        print("  2. Use Supabase API for rentals")
        print("  3. Run password reset bot with cloud sync")
        print("\n" + "="*60)
        
        return True
        
    except FileNotFoundError as e:
        if "supabase_config.json" in str(e):
            print("\n✗ Error: config/supabase_config.json not found!")
            print("\nPlease:")
            print("1. Create Supabase account at https://supabase.com")
            print("2. Get your API credentials")
            print("3. Update config/supabase_config.json")
            print("4. Run this script again")
        else:
            print(f"\n✗ Error: {e}")
        return False
        
    except Exception as e:
        print(f"\n✗ Migration failed: {e}")
        print("\nMake sure:")
        print("1. You've run the SQL schema (supabase_schema.sql)")
        print("2. Your Supabase credentials are correct")
        print("3. Local database exists at database/rental_system.db")
        return False


if __name__ == "__main__":
    import sys
    success = migrate_to_supabase()
    sys.exit(0 if success else 1)
