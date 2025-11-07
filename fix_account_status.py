"""
Fix account statuses in Supabase
"""
from src.supabase_db import SupabaseDB
from datetime import datetime

print("\n" + "="*80)
print("FIXING ACCOUNT STATUSES")
print("="*80 + "\n")

db = SupabaseDB()

# Fix vpbgkt - remove old 'rented' status
print("1. Fixing vpbgkt (removing old rental status)...")
db.client.table('accounts').update({
    'status': 'available',
    'rented_at': None,
    'available_at': datetime.now().isoformat()
}).eq('id', 1).execute()
print("   ✓ vpbgkt marked as available")

# Fix rameshkumawat - mark as exception (wrong password)
print("\n2. Fixing rameshkumawat (marking as exception - wrong password)...")
db.mark_account_exception(2, 'wrong_password_detected')
print("   ✓ rameshkumawat marked as exception")

# Show updated statuses
print("\n" + "="*80)
print("UPDATED ACCOUNT STATUSES")
print("="*80 + "\n")

accounts = db.client.table('accounts').select('id, username, status, exception_reason, failed_login_attempts').execute()

for acc in accounts.data:
    status_icon = "🟢" if acc['status'] == 'available' else "🔴" if acc['status'] == 'exception' else "🔵"
    print(f"{status_icon} {acc['username']} (ID: {acc['id']})")
    print(f"   Status: {acc['status']}")
    if acc['exception_reason']:
        print(f"   Exception: {acc['exception_reason']}")
        print(f"   Failed attempts: {acc['failed_login_attempts']}")
    print()

# Show statistics
print("="*80)
print("STATISTICS")
print("="*80 + "\n")

stats = db.get_dashboard_stats()
print(f"   Total Accounts: {stats['total_accounts']}")
print(f"   Available: {stats['available_accounts']} 🟢")
print(f"   Rented: {stats['rented_accounts']} 🔵")
print(f"   Exceptions: {stats['exception_accounts']} 🔴")

print("\n" + "="*80)
print("✓ DONE - Status corrected!")
print("="*80 + "\n")

print("Next steps:")
print("  1. Fix rameshkumawat password in config/accounts.json")
print("  2. Run: python manage_exceptions.py --reset 2 --password <correct_password>")
print("  3. Or manually update config and run password reset again")
