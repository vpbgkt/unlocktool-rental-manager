"""
Quick API Test - Shows you how to use your API
"""
import requests
import json

# API Configuration
BASE_URL = "http://localhost:5000/api"

print("\n" + "="*70)
print(" 🔑 API KEY SETUP")
print("="*70)
print("\n⚠️  You need your API key to continue!")
print("\nYour API key was displayed when you created 'Vishal main api'")
print("It looks like: urt_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
print("\nOptions to find it:")
print("  1. Check your PowerShell terminal history")
print("  2. Create a new API key if you lost it")
print("  3. Use 'Demo Customer Portal' key for testing")

# Let's use the Demo Customer Portal key for demonstration
print("\n" + "="*70)
print(" 📝 FOR NOW, LET'S TEST WITH DEMO KEY")
print("="*70)

API_KEY = input("\nEnter your API key (or press Enter to skip): ").strip()

if not API_KEY:
    print("\n✓ No problem! Let me show you the commands to use:")
    print("\n" + "="*70)
    print(" 📋 HOW TO USE YOUR API KEY")
    print("="*70)
    
    print("\n1️⃣  TEST API HEALTH (No key needed)")
    print("   curl http://localhost:5000/api/health")
    
    print("\n2️⃣  LIST AVAILABLE ACCOUNTS")
    print('   curl -H "X-API-Key: YOUR_KEY_HERE" http://localhost:5000/api/accounts/available?website=unlocktool')
    
    print("\n3️⃣  RENT AN ACCOUNT")
    print('   curl -X POST http://localhost:5000/api/accounts/rent \\')
    print('     -H "X-API-Key: YOUR_KEY_HERE" \\')
    print('     -H "Content-Type: application/json" \\')
    print('     -d "{\\"website\\":\\"unlocktool\\",\\"customer_info\\":\\"My Customer\\"}"')
    
    print("\n4️⃣  CHECK ACCOUNT STATUS")
    print('   curl -H "X-API-Key: YOUR_KEY_HERE" http://localhost:5000/api/accounts/status/1')
    
    print("\n5️⃣  RETURN ACCOUNT")
    print('   curl -X POST http://localhost:5000/api/accounts/return/1 \\')
    print('     -H "X-API-Key: YOUR_KEY_HERE"')
    
    print("\n6️⃣  VIEW YOUR STATISTICS")
    print('   curl -H "X-API-Key: YOUR_KEY_HERE" "http://localhost:5000/api/stats/me?days=30"')
    
    print("\n" + "="*70)
    print(" 📖 READ THE COMPLETE GUIDE")
    print("="*70)
    print("\n   cat HOW_TO_USE_API.md")
    print("   cat API_GUIDE.md")
    print("\n" + "="*70)
    
else:
    # Test the API with the provided key
    headers = {
        "X-API-Key": API_KEY,
        "Content-Type": "application/json"
    }
    
    print("\n" + "="*70)
    print(" 🧪 TESTING API WITH YOUR KEY")
    print("="*70)
    
    # Test 1: Health check
    print("\n1️⃣  Testing API Health...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 2: List available accounts
    print("\n2️⃣  Listing Available Accounts...")
    try:
        response = requests.get(
            f"{BASE_URL}/accounts/available?website=unlocktool",
            headers=headers,
            timeout=5
        )
        print(f"   Status: {response.status_code}")
        data = response.json()
        print(f"   Response: {json.dumps(data, indent=2)}")
        
        if data.get('success') and data.get('available_count', 0) > 0:
            print(f"\n   ✅ Found {data['available_count']} available account(s)")
            
            # Test 3: Rent an account
            print("\n3️⃣  Renting an Account...")
            rent_data = {
                "website": "unlocktool",
                "customer_info": "API Test Customer"
            }
            response = requests.post(
                f"{BASE_URL}/accounts/rent",
                headers=headers,
                json=rent_data,
                timeout=5
            )
            print(f"   Status: {response.status_code}")
            rent_result = response.json()
            print(f"   Response: {json.dumps(rent_result, indent=2)}")
            
            if rent_result.get('success'):
                account_id = rent_result['account']['id']
                print(f"\n   ✅ Successfully rented account!")
                print(f"   📧 Username: {rent_result['account']['username']}")
                print(f"   🔒 Password: {rent_result['account']['password']}")
                print(f"   ⏰ Expires: {rent_result['account']['expires_at']}")
                
                # Test 4: Check status
                print(f"\n4️⃣  Checking Account Status...")
                response = requests.get(
                    f"{BASE_URL}/accounts/status/{account_id}",
                    headers=headers,
                    timeout=5
                )
                print(f"   Status: {response.status_code}")
                print(f"   Response: {json.dumps(response.json(), indent=2)}")
                
                # Test 5: Return account
                print(f"\n5️⃣  Returning Account...")
                response = requests.post(
                    f"{BASE_URL}/accounts/return/{account_id}",
                    headers=headers,
                    timeout=5
                )
                print(f"   Status: {response.status_code}")
                print(f"   Response: {json.dumps(response.json(), indent=2)}")
                
                # Test 6: View statistics
                print(f"\n6️⃣  Viewing Usage Statistics...")
                response = requests.get(
                    f"{BASE_URL}/stats/me?days=7",
                    headers=headers,
                    timeout=5
                )
                print(f"   Status: {response.status_code}")
                print(f"   Response: {json.dumps(response.json(), indent=2)}")
                
                print("\n" + "="*70)
                print(" ✅ ALL TESTS COMPLETED SUCCESSFULLY!")
                print("="*70)
                print("\nYour API is working perfectly! 🎉")
        else:
            print("\n   ℹ️  No accounts available for rental right now")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n" + "="*70)
