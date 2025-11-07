# 🚀 How to Use Your API Key - Complete Guide

## ✅ Your API Key Info
- **Name**: Vishal main api
- **ID**: 3
- **Rate Limit**: 100 requests/day
- **Status**: Active
- **Created**: 2025-11-07 08:03:58

⚠️ **IMPORTANT**: The full API key was displayed when you created it. 
Check your PowerShell history or the `customer_api_keys.txt` file.

---

## 📋 Step-by-Step Usage Guide

### STEP 1: Start the API Server

Open a new terminal and run:
```powershell
.\venv\Scripts\python.exe api_server.py
```

The server will start on: **http://localhost:5000**

---

### STEP 2: Test the API (Health Check)

```powershell
# This doesn't require API key
curl http://localhost:5000/api/health
```

Expected response:
```json
{"status":"ok","message":"API is running"}
```

---

### STEP 3: Use Your API Key

Replace `YOUR_API_KEY_HERE` with the actual key from when you created it.

#### 📌 Example 1: List Available Accounts

```powershell
curl -H "X-API-Key: YOUR_API_KEY_HERE" http://localhost:5000/api/accounts/available?website=unlocktool
```

**Expected Response:**
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

#### 📌 Example 2: Rent an Account

```powershell
curl -X POST http://localhost:5000/api/accounts/rent -H "X-API-Key: YOUR_API_KEY_HERE" -H "Content-Type: application/json" -d "{\"website\":\"unlocktool\",\"customer_info\":\"My Customer\"}"
```

**Expected Response:**
```json
{
  "success": true,
  "account": {
    "id": 1,
    "username": "vpbgkt",
    "password": "5NP@VsaqeBy6mYGy",
    "email": "vpbgkt@gmail.com",
    "website": "unlocktool",
    "rented_at": "2025-11-07 08:10:00",
    "expires_at": "2025-11-07 14:10:00"
  }
}
```

---

#### 📌 Example 3: Check Account Status

```powershell
curl -H "X-API-Key: YOUR_API_KEY_HERE" http://localhost:5000/api/accounts/status/1
```

**Expected Response:**
```json
{
  "success": true,
  "account_id": 1,
  "status": "rented",
  "rented_at": "2025-11-07 08:10:00",
  "expires_at": "2025-11-07 14:10:00",
  "remaining_minutes": 320
}
```

---

#### 📌 Example 4: Return an Account Early

```powershell
curl -X POST http://localhost:5000/api/accounts/return/1 -H "X-API-Key: YOUR_API_KEY_HERE"
```

**Expected Response:**
```json
{
  "success": true,
  "message": "Account returned successfully",
  "account_id": 1
}
```

---

#### 📌 Example 5: View Your Usage Statistics

```powershell
curl -H "X-API-Key: YOUR_API_KEY_HERE" "http://localhost:5000/api/stats/me?days=30"
```

**Expected Response:**
```json
{
  "success": true,
  "stats": {
    "total_requests": 5,
    "accounts_rented": 2,
    "accounts_returned": 1,
    "unique_accounts": 1,
    "period_days": 30
  }
}
```

---

## 🐍 Using Python

Create a test script:

```python
import requests

# Your API key
API_KEY = "urt_your_actual_key_here"
BASE_URL = "http://localhost:5000/api"

headers = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}

# 1. List available accounts
print("1. Checking available accounts...")
response = requests.get(f"{BASE_URL}/accounts/available?website=unlocktool", headers=headers)
print(response.json())

# 2. Rent an account
print("\n2. Renting an account...")
data = {"website": "unlocktool", "customer_info": "Test Customer"}
response = requests.post(f"{BASE_URL}/accounts/rent", json=data, headers=headers)
account = response.json()

if account['success']:
    print(f"✅ Rented account!")
    print(f"   Username: {account['account']['username']}")
    print(f"   Password: {account['account']['password']}")
    print(f"   Expires: {account['account']['expires_at']}")
    
    account_id = account['account']['id']
    
    # 3. Check status
    print(f"\n3. Checking status...")
    response = requests.get(f"{BASE_URL}/accounts/status/{account_id}", headers=headers)
    print(response.json())
    
    # 4. Return account
    print(f"\n4. Returning account...")
    response = requests.post(f"{BASE_URL}/accounts/return/{account_id}", headers=headers)
    print(response.json())

# 5. View statistics
print("\n5. Viewing statistics...")
response = requests.get(f"{BASE_URL}/stats/me?days=7", headers=headers)
print(response.json())
```

---

## 🔍 Where to Find Your Full API Key?

Your full API key was displayed when you created it. Check these places:

### Option 1: PowerShell History
```powershell
Get-History | Select-Object -Last 50
```

### Option 2: Check customer_api_keys.txt
```powershell
cat customer_api_keys.txt
```

### Option 3: Database Query
```powershell
.\venv\Scripts\python.exe -c "from src.database import Database; db = Database(); import sqlite3; conn = sqlite3.connect('database/rental_system.db'); cursor = conn.cursor(); cursor.execute('SELECT api_key_hash FROM api_keys WHERE id=3'); print(cursor.fetchone())"
```

⚠️ **Note**: API keys are hashed in the database for security. You can only see the full key when it's first created.

---

## 📊 Monitor Your API Usage

```powershell
# View all your API keys
.\venv\Scripts\python.exe show_api_keys.py

# Manage API keys (view details, usage, etc.)
.\venv\Scripts\python.exe manage_api_keys.py
```

---

## 🎯 Common Use Cases

### Use Case 1: Customer Portal Integration
Your customer portal calls the API to rent accounts for end users:
1. Customer logs into your portal
2. Portal calls `/api/accounts/rent` with your API key
3. Portal displays username/password to customer
4. Account auto-expires after 6 hours
5. Portal can call `/api/accounts/return` if customer finishes early

### Use Case 2: Automated Reselling
Script that automatically rents and sells accounts:
1. Monitor available accounts
2. When order received, rent account via API
3. Deliver credentials to customer
4. Track usage and earnings

### Use Case 3: Multi-Customer Management
You create separate API keys for each customer:
- Customer A: 50 requests/day limit
- Customer B: 100 requests/day limit
- Customer C: 500 requests/day limit
- Track each customer's usage separately

---

## 🔒 Security Best Practices

1. **Never commit API keys to git**
2. **Store keys in environment variables**
3. **Use different keys for testing and production**
4. **Revoke compromised keys immediately**
5. **Monitor usage regularly for suspicious activity**

---

## 🆘 Troubleshooting

### Error: "Invalid API key"
- Check you're using the full API key (starts with `urt_`)
- Verify the key is active: `.\venv\Scripts\python.exe show_api_keys.py`

### Error: "Rate limit exceeded"
- You've hit your daily limit (100 requests/day)
- Wait until next day or increase limit via `manage_api_keys.py`

### Error: "No available accounts"
- All accounts are currently rented
- Wait for accounts to expire or be returned
- Add more accounts to the system

---

## 📞 Need Help?

Run these commands for more info:
```powershell
# View comprehensive API guide
cat API_GUIDE.md

# View customer management guide
cat API_CUSTOMER_GUIDE.md

# Test the API
.\venv\Scripts\python.exe test_api_client.py
```
