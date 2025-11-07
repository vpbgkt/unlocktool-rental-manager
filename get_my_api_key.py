"""Get details of the newly created API key"""
from src.api_manager import APIManager

api = APIManager()
keys = api.get_api_keys()

# Find the newest key
newest = keys[0]
for k in keys:
    if k['name'] == 'Vishal main api':
        newest = k
        break

print("\n" + "="*70)
print(" YOUR API KEY DETAILS")
print("="*70)
print(f"\nName: {newest['name']}")
print(f"ID: {newest['id']}")
print(f"Status: {newest['status']}")
print(f"Rate Limit: {newest['rate_limit']} requests/day")
print(f"Total Requests: {newest['total_requests']}")
print(f"Created: {newest['created_at']}")
print(f"\nAPI Key Preview: {newest['api_key_preview']}")
print("\n⚠️  Note: Full API key is only shown once during creation")
print("   Check your terminal history or customer_api_keys.txt")
print("\n" + "="*70)
