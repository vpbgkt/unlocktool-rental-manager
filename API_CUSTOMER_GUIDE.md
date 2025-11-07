# 🔑 API Management - Complete Guide

## TL;DR - Quick Start

```bash
# 1. Create API key for a customer
.\venv\Scripts\python.exe manage_api_keys.py
# Choose: 1, enter customer details

# 2. View all API keys
.\venv\Scripts\python.exe manage_api_keys.py
# Choose: 2

# 3. Track customer usage
.\venv\Scripts\python.exe manage_api_keys.py
# Choose: 3, enter API key ID
```

---

## 🎯 What You Have

### Already Built & Working:

1 **API Key Generation** - Create unique keys
2. **Usage Tracking** - Every request logged
3. **Rate Limiting** - Requests per day limit
4. **Activity Logs** - Full audit trail
5. **Statistics** - Per-key analytics
6. **Revocation** - Disable keys anytime

---

## 📋 Step-by-Step: Give API to Customer

### Step 1: Create API Key

```bash
.\venv\Scripts\python.exe manage_api_keys.py
```

Choose `1` and enter:
- **Name**: `Customer Name` or `Their Website`
- **Email**: `customer@example.com`
- **Rate Limit**: `100` (requests per day)
- **Notes**: `Premium plan` or whatever

**You'll get:**
```
🔑 API KEY:
urt_xYz123AbC456...

⚠️ Copy this! Can't retrieve it later!
```

### Step 2: Send to Customer

Email them:
```
Hi [Customer],

Your API key: urt_xYz123AbC456...

API Base URL: http://your-server:5000

Documentation: [link to API_GUIDE.md]

Rate Limit: 100 requests/day

Regards
```

### Step 3: Track Their Usage

```bash
.\venv\Scripts\python.exe manage_api_keys.py
```

Choose `3`, enter their API key ID

**You'll see:**
```
Total Requests: 45
Rentals: 15
Returns: 12
Unique Accounts: 3
```

---

## 📊 How Tracking Works

### Every API Call Gets Logged:

| Field | What It Tracks |
|-------|---------------|
| **API Key ID** | Which customer |
| **Action** | rent / return / check |
| **Account** | Which account used |
| **Website** | unlocktool / androidmultitool |
| **Timestamp** | When it happened |
| **IP Address** | Where from |
| **Status** | success / error |

### Example Tracking:

```
Customer "John's Website" (API Key ID: 5)
  2025-11-07 10:00 - RENT   - vpbgkt - success
  2025-11-07 12:00 - CHECK  - vpbgkt - success
  2025-11-07 16:00 - RETURN - vpbgkt - success
  
Total: 3 requests, 1 rental
```

---

## 🎚️ Setting Limits

### Rate Limit (Already Works):

When creating key, set **Rate Limit**:
- **50** = 50 requests/day
- **100** = 100 requests/day
- **1000** = 1000 requests/day (premium)

Customer gets blocked when limit reached.

---

## 💡 Business Models

### Option 1: Tiered Plans

**Basic** - $10/month
- 100 requests/day
- 5 rentals/day

**Pro** - $30/month
- 500 requests/day
- 20 rentals/day

**Enterprise** - Custom
- Unlimited requests
- Unlimited rentals

### Option 2: Pay Per Use

- $2 per account rental
- Count rentals via tracking
- Bill monthly

### Option 3: Subscription + Overage

- $20/month (includes 10 rentals)
- $1.50 per additional rental

---

## 🔍 Monitoring Customers

### View All Customers:

```bash
.\venv\Scripts\python.exe manage_api_keys.py
# Choose: 2
```

Shows:
- Active keys
- Total requests
- Last used
- Status

### View Specific Customer:

```bash
.\venv\Scripts\python.exe manage_api_keys.py
# Choose: 3, enter ID
```

Shows:
- Total rentals
- Accounts used
- Recent activity
- Success rate

### View Recent Activity:

```bash
.\venv\Scripts\python.exe manage_api_keys.py
# Choose: 6
```

Shows last 20 API calls across all customers.

---

## 🚫 Revoking Access

Customer didn't pay? Revoke their key:

```bash
.\venv\Scripts\python.exe manage_api_keys.py
# Choose: 4, enter ID
```

Their API key stops working immediately!

---

## 📈 Reports You Can Generate

### 1. Revenue Report

Count rentals per customer × your price:
```python
# Example: Customer 5 made 15 rentals at $2 each
15 rentals × $2 = $30 revenue
```

### 2. Popular Accounts

Which accounts get rented most?
Track via `api_usage` table, group by `account_id`.

### 3. Peak Times

When do customers rent most?
Track `timestamp` patterns in `api_usage`.

### 4. Website Popularity

unlocktool vs androidmultitool?
Group by `website` in `api_usage`.

---

## 🔒 Security

Already implemented:
- ✅ Keys hashed (SHA256)
- ✅ Secure generation (cryptographic random)
- ✅ Header-based auth (`X-API-Key`)
- ✅ IP logging
- ✅ Audit trail

---

## 📞 Customer API Documentation

Give this to customers:

```bash
# Get available accounts
curl http://your-server:5000/api/accounts/available?website=unlocktool \
  -H "X-API-Key: YOUR_KEY"

# Rent an account
curl -X POST http://your-server:5000/api/accounts/rent \
  -H "X-API-Key: YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{"website": "unlocktool"}'

# Returns:
{
  "success": true,
  "account": {
    "username": "vpbgkt",
    "password": "abc123",
    "expires_at": "2025-11-07 19:00:00"
  }
}

# Check status
curl http://your-server:5000/api/accounts/status/1 \
  -H "X-API-Key: YOUR_KEY"

# Return early
curl -X POST http://your-server:5000/api/accounts/return/1 \
  -H "X-API-Key: YOUR_KEY"

# View your stats
curl http://your-server:5000/api/stats/me \
  -H "X-API-Key: YOUR_KEY"
```

---

## 🎯 Summary

### To Give API to Customer:
1. Run `manage_api_keys.py`
2. Create new key
3. Copy the key
4. Send to customer
5. Monitor their usage

### To Track Usage:
1. Run `manage_api_keys.py`
2. View API key details (option 3)
3. See rentals, requests, activity

### To Set Limits:
- **Rate Limit** when creating key (already works)
- **Account Limits** - Coming in next update!

### To Charge:
- Count rentals from tracking
- Multiply by your price
- Bill monthly

---

## 🚀 Try It Now!

```bash
# Create your first customer API key
.\venv\Scripts\python.exe manage_api_keys.py
```

Choose option 1 and create a test key!

Then test it:
```bash
# Start API server
.\venv\Scripts\python.exe api_server.py

# In another terminal, test the API
curl http://localhost:5000/api/accounts/available?website=unlocktool \
  -H "X-API-Key: urt_74O0lEd-kHWsM_oD8-ngz6uUiluJtha05gru1L_rwFY"
```

---

**You have a complete API management system!** 🎉

Everything for tracking customers and limiting access is already built and working!
