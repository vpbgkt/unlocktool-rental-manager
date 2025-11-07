# ✅ API WORKING! - Quick Reference

## 🎉 Your API Test Just Succeeded!

```
✅ Health check: OK
✅ Listed accounts: 1 available (vpbgkt)
✅ Rented account: Success!
   Username: vpbgkt
   Password: 5NP@VsaqeBy6mYGy
   Expires: 2025-11-07 19:41:43
```

---

## 🚀 HOW TO USE (3 Ways)

### 1️⃣ Use The Working Test Script

```powershell
.\venv\Scripts\python.exe test_api_client.py
```
✅ This already works with your API key!

### 2️⃣ PowerShell cURL

```powershell
# List accounts
curl -H "X-API-Key: YOUR_KEY" http://localhost:5000/api/accounts/available?website=unlocktool

# Rent account
$headers = @{"X-API-Key"="YOUR_KEY"; "Content-Type"="application/json"}
$body = '{"website":"unlocktool","customer_info":"Customer"}'
Invoke-RestMethod -Method POST -Uri http://localhost:5000/api/accounts/rent -Headers $headers -Body $body
```

### 3️⃣ Custom Python Script

```python
import requests

API_KEY = "urt_your_key_here"
headers = {"X-API-Key": API_KEY}

# Rent account
response = requests.post(
    "http://localhost:5000/api/accounts/rent",
    json={"website": "unlocktool", "customer_info": "Test"},
    headers=headers
)
account = response.json()
print(f"Username: {account['account']['username']}")
print(f"Password: {account['account']['password']}")
```

---

## 🔑 Your API Keys (3 available)

```powershell
# View all keys
.\venv\Scripts\python.exe show_api_keys.py

# Create new key for customer
.\venv\Scripts\python.exe manage_api_keys.py
# Choose: 1 (Create new)
```

---

## 📊 Monitor Usage

```powershell
.\venv\Scripts\python.exe manage_api_keys.py
# Choose: 3 (View details) or 5 (Statistics)
```

---

## 🎯 Give to Customer

1. Create API key (manage_api_keys.py → option 1)
2. Save the key shown (urt_...)
3. Send customer:
   - API Key
   - Base URL: http://your-server:5000/api
   - Documentation: API_GUIDE.md

---

## ⚡ Server Status

- **Running**: http://localhost:5000 ✅
- **Database**: Supabase connected ✅
- **Accounts**: 1 available (vpbgkt) ✅

---

**That's it! Your API is ready to use! 🚀**
