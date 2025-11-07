"""
Quick Demo - Show API Keys and Create New One
"""
from src.api_manager import APIManager

api = APIManager()

print("\n" + "="*70)
print(" YOUR API KEYS")
print("="*70)

keys = api.get_api_keys()

if not keys:
    print("\n❌ No API keys found yet!")
    print("\n💡 Create your first API key:")
    print("   .\venv\Scripts\python.exe manage_api_keys.py")
else:
    print(f"\n✓ You have {len(keys)} API key(s):\n")
    for i, key in enumerate(keys, 1):
        status_icon = "✓" if key['status'] == 'active' else "✗"
        print(f"{i}. {status_icon} {key['name']} (ID: {key['id']})")
        print(f"   Requests: {key['total_requests']} / {key['rate_limit']} per day")
        print(f"   Status: {key['status']}")
        print(f"   Last Used: {key['last_used'] or 'Never'}")
        print()

print("="*70)
print(" QUICK ACTIONS")
print("="*70)
print("\n1. Create new API key:")
print("   .\venv\Scripts\python.exe manage_api_keys.py")
print("\n2. View usage details:")
print("   .\venv\Scripts\python.exe manage_api_keys.py")
print("   (Choose option 3)")
print("\n3. Test API:")
print("   .\venv\Scripts\python.exe api_server.py")
print("="*70 + "\n")
