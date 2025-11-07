# 🎯 QUICK START: Using Your API Key

## ✅ YOUR SETUP
- **API Server**: Running on http://localhost:5000
- **Your API Key**: "Vishal main api" (ID: 3)
- **Rate Limit**: 100 requests/day
- **Available Accounts**: 1 (vpbgkt)

---

## 🚀 STEP-BY-STEP USAGE

### STEP 1: Find Your API Key

Your API key was displayed when you created it in `manage_api_keys.py`.
It looks like: `urt_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

**Can't find it?** Create a new one:
```powershell
.\venv\Scripts\python.exe manage_api_keys.py
# Choose option 1, enter a name, and save the key that's displayed
```

---

### STEP 2: Test the API (Without Key)

```powershell
curl http://localhost:5000/api/health
```

**Expected:**
```json
{"status":"ok","message":"API is running"}
```

---

### STEP 3: Use Your API Key

Replace `YOUR_API_KEY` with your actual key in the commands below.

#### 🔹 List Available Accounts

```powershell
curl -H "X-API-Key: YOUR_API_KEY" http://localhost:5000/api/accounts/available?website=unlocktool
```

**You'll see:**
```json
{
  "success": true,
  "available_count": 1,
  "accounts": [
    {
      "id": 1,
      "username": "vpbgkt",
      "website": "unlocktool"
    }
  ]
}
```

---

#### 🔹 Rent an Account

```powershell
curl -X POST http://localhost:5000/api/accounts/rent -H "X-API-Key: YOUR_API_KEY" -H "Content-Type: application/json" -d "{\"website\":\"unlocktool\",\"customer_info\":\"Test Customer\"}"
```

**You'll get credentials:**
```json
{
  "success": true,
  "account": {
    "id": 1,
    "username": "vpbgkt",
    "password": "5NP@VsaqeBy6mYGy",
    "email": "vpbgkt@gmail.com",
    "website": "unlocktool",
    "rented_at": "2025-11-07 08:30:00",
    "expires_at": "2025-11-07 14:30:00"
  }
}
```

---

#### 🔹 Check Status

```powershell
curl -H "X-API-Key: YOUR_API_KEY" http://localhost:5000/api/accounts/status/1
```

---

#### 🔹 Return Early (Optional)

```powershell
curl -X POST http://localhost:5000/api/accounts/return/1 -H "X-API-Key: YOUR_API_KEY"
```

---

#### 🔹 View Your Stats

```powershell
curl -H "X-API-Key: YOUR_API_KEY" "http://localhost:5000/api/stats/me?days=7"
```

---

## 🐍 Python Example

Save this as `test_my_api.py`:

```python
import requests

# REPLACE THIS with your actual API key
API_KEY = "urt_your_actual_key_here"

BASE_URL = "http://localhost:5000/api"
headers = {"X-API-Key": API_KEY}

# 1. List available accounts
print("📋 Available accounts:")
response = requests.get(f"{BASE_URL}/accounts/available?website=unlocktool", headers=headers)
print(response.json())

# 2. Rent an account
print("\n🔑 Renting account:")
data = {"website": "unlocktool", "customer_info": "My Customer"}
response = requests.post(f"{BASE_URL}/accounts/rent", json=data, headers=headers)
account = response.json()

if account['success']:
    print(f"✅ Username: {account['account']['username']}")
    print(f"✅ Password: {account['account']['password']}")
    print(f"✅ Expires: {account['account']['expires_at']}")
    
    # 3. Check status
    account_id = account['account']['id']
    response = requests.get(f"{BASE_URL}/accounts/status/{account_id}", headers=headers)
    print(f"\n📊 Status: {response.json()}")
    
    # 4. Return account
    response = requests.post(f"{BASE_URL}/accounts/return/{account_id}", headers=headers)
    print(f"\n↩️  Returned: {response.json()}")

# 5. View stats
response = requests.get(f"{BASE_URL}/stats/me?days=7", headers=headers)
print(f"\n📈 Your stats: {response.json()}")
```

Then run:
```powershell
.\venv\Scripts\python.exe test_my_api.py
```

---

## 🎯 WHAT YOU CAN DO

### For Testing:
1. ✅ API server is running (http://localhost:5000)
2. ✅ You have an API key created
3. ✅ You have 1 available account (vpbgkt)
4. ✅ Test with curl or Python
5. ✅ Monitor usage with `manage_api_keys.py`

### For Customers:
1. Give them the API key
2. Give them the API documentation (API_GUIDE.md)
3. They call your API to rent accounts
4. You track their usage in the database
5. You can set rate limits per customer

### For Business:
1. Create different API keys for different customers
2. Set different rate limits (50/day, 100/day, 500/day)
3. Track usage: `.\venv\Scripts\python.exe manage_api_keys.py` (option 5)
4. Monitor activity: `.\venv\Scripts\python.exe manage_api_keys.py` (option 6)
5. Revoke keys if needed

---

## 🔍 FIND YOUR API KEY

### Option 1: Check Terminal History
Scroll up in your PowerShell terminal to where you created the key.

### Option 2: Create New Key for Testing
```powershell
.\venv\Scripts\python.exe manage_api_keys.py
# Choose: 1 (Create new API key)
# Name: "Test Key"
# Rate Limit: 100
# Copy the key it displays
```

### Option 3: Use Existing Demo Key
Run this to see if you have other keys:
```powershell
.\venv\Scripts\python.exe show_api_keys.py
```

You have a "Demo Customer Portal" key with ID: 2 that has 21 requests already!

---

## ⚡ QUICK TEST RIGHT NOW

Run this simple test (no API key needed for health check):

```powershell
curl http://localhost:5000/api/health
```

If you see `{"status":"ok"}` - your API is working! ✅

---

## 📖 MORE HELP

- **Complete Guide**: `cat HOW_TO_USE_API.md`
- **API Reference**: `cat API_GUIDE.md`
- **Customer Guide**: `cat API_CUSTOMER_GUIDE.md`
- **Manage Keys**: `.\venv\Scripts\python.exe manage_api_keys.py`
- **View Keys**: `.\venv\Scripts\python.exe show_api_keys.py`

---

## 🎉 YOU'RE READY!

Your API is live and ready to use. Just need to:
1. Find your API key (or create a new test key)
2. Try the curl commands above
3. Start renting accounts via API!
