"""
Check and manually expire old rentals
"""
from src.supabase_db import SupabaseDB
from datetime import datetime

print("\n" + "="*80)
print("CHECKING EXPIRED RENTALS")
print("="*80 + "\n")

db = SupabaseDB()

# Get all active rentals
result = db.client.table('rentals').select('*, accounts(id, username)').eq('status', 'active').execute()

if not result.data:
    print("✅ No active rentals found")
else:
    now = datetime.now()
    print(f"Current time: {now.strftime('%Y-%m-%d %H:%M:%S')}\n")
    print(f"Found {len(result.data)} active rental(s):\n")
    
    expired_count = 0
    
    for rental in result.data:
        account = rental['accounts']
        expires_at = datetime.fromisoformat(rental['expires_at'].replace('Z', '+00:00'))
        
        # Calculate time difference
        time_diff = expires_at - now
        hours_remaining = time_diff.total_seconds() / 3600
        
        is_expired = expires_at < now
        
        print(f"Rental ID: {rental['id']}")
        print(f"  Account: {account['username']} (ID: {account['id']})")
        print(f"  Customer: {rental.get('customer_name', 'Unknown')}")
        print(f"  Rented at: {rental['rented_at']}")
        print(f"  Expires at: {rental['expires_at']}")
        print(f"  Status: {'🔴 EXPIRED' if is_expired else '🟢 ACTIVE'}")
        
        if is_expired:
            hours_ago = abs(hours_remaining)
            print(f"  ⚠️ Expired {hours_ago:.1f} hours ago!")
            
            # Ask to expire it
            print(f"\n  Would you like to expire this rental? (yes/no): ", end='')
            response = input().strip().lower()
            
            if response in ['yes', 'y']:
                # Mark rental as expired
                db.client.table('rentals').update({
                    'status': 'expired',
                    'returned_at': now.isoformat()
                }).eq('id', rental['id']).execute()
                
                # Mark account as available
                db.client.table('accounts').update({
                    'status': 'available',
                    'available_at': now.isoformat()
                }).eq('id', account['id']).execute()
                
                print(f"  ✅ Rental {rental['id']} marked as expired")
                print(f"  ✅ Account {account['username']} marked as available")
                expired_count += 1
            else:
                print(f"  ⏭️ Skipped")
        else:
            print(f"  Time remaining: {hours_remaining:.1f} hours")
        
        print()
    
    print("="*80)
    print(f"Summary: {expired_count} rental(s) expired")
    print("="*80 + "\n")

# Show updated statistics
print("\n📊 Updated Statistics:")
stats = db.get_dashboard_stats()
print(f"   Total Accounts: {stats['total_accounts']}")
print(f"   Available: {stats['available_accounts']} 🟢")
print(f"   Rented: {stats['rented_accounts']} 🔵")
print(f"   Exceptions: {stats['exception_accounts']} 🔴")
print()
