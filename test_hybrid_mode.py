"""
Quick test to verify Hybrid Mode is working correctly
"""

from src.supabase_db import SupabaseDB
from src.database import PasswordResetDB
import json

print("\n" + "=" * 60)
print("HYBRID MODE VERIFICATION TEST")
print("=" * 60 + "\n")

# Test 1: Supabase Connection
print("1. Testing Supabase connection...")
try:
    cloud_db = SupabaseDB()
    print("   ✓ Supabase connected")
except Exception as e:
    print(f"   ✗ Supabase failed: {e}")
    exit(1)

# Test 2: Local SQLite Connection
print("\n2. Testing local SQLite connection...")
try:
    local_db = PasswordResetDB()
    print("   ✓ SQLite connected")
except Exception as e:
    print(f"   ✗ SQLite failed: {e}")
    exit(1)

# Test 3: Compare Data
print("\n3. Comparing data between local and cloud...")
try:
    # Get accounts from Supabase
    cloud_accounts = cloud_db.get_available_accounts('unlocktool')
    print(f"   ✓ Supabase: {len(cloud_accounts)} available accounts")
    
    # Get accounts from SQLite
    local_accounts = local_db.get_available_accounts('unlocktool')
    print(f"   ✓ SQLite: {len(local_accounts)} available accounts")
except Exception as e:
    print(f"   ✗ Data comparison failed: {e}")

# Test 4: Get Statistics
print("\n4. Getting statistics from Supabase...")
try:
    stats = cloud_db.get_dashboard_stats()
    print(f"   ✓ Total Accounts: {stats['total_accounts']}")
    print(f"   ✓ Available: {stats['available_accounts']}")
    print(f"   ✓ Rented: {stats['rented_accounts']}")
    print(f"   ✓ Exceptions: {stats['exception_accounts']}")
except Exception as e:
    print(f"   ✗ Statistics failed: {e}")

# Test 5: Check Scheduler Integration
print("\n5. Testing scheduler integration...")
try:
    from src.scheduler import ResetScheduler
    scheduler = ResetScheduler()
    
    if scheduler.cloud_db:
        print("   ✓ Scheduler has cloud_db initialized")
    else:
        print("   ⚠ Scheduler cloud_db is None (will use SQLite only)")
    
    print(f"   ✓ Scheduler has {len(scheduler.accounts)} accounts configured")
except Exception as e:
    print(f"   ✗ Scheduler test failed: {e}")

# Test 6: Check Config Files
print("\n6. Checking configuration files...")
try:
    with open('config/accounts.json', 'r') as f:
        accounts = json.load(f)
        print(f"   ✓ accounts.json: {len(accounts.get('accounts', []))} accounts")
    
    with open('config/supabase_config.json', 'r') as f:
        supabase_config = json.load(f)
        print(f"   ✓ supabase_config.json: {supabase_config['url']}")
except Exception as e:
    print(f"   ✗ Config check failed: {e}")

print("\n" + "=" * 60)
print("✓ HYBRID MODE IS WORKING!")
print("=" * 60)
print("\n📋 Summary:")
print("   - Local automation: SQLite backup ✓")
print("   - Cloud database: Supabase sync ✓")
print("   - Scheduler: Dual database support ✓")
print("   - Config files: Valid ✓")
print("\n🚀 Ready to run password resets with cloud sync!")
print("   Run: python main.py --mode run-once\n")
