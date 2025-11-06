# API Management Quick Start Guide

## Overview
Your tool rental system now has a complete REST API with:
- **API Key Management** - Create and manage API keys for customers
- **Account Rental** - Rent available accounts via API
- **Usage Tracking** - Monitor which API keys are using which accounts
- **Auto-expiry** - Accounts automatically become available after validity period

## Installation

1. **Install new dependencies:**
```bash
.\venv\Scripts\python.exe -m pip install flask flask-cors
```

## Setup

### 1. Create API Keys

Run the API key management tool:
```bash
.\venv\Scripts\python.exe manage_api_keys.py
```

Choose option 1 to create a new API key. Example:
- Name: "Customer Portal"
- Email: customer@example.com
- Rate Limit: 100 (requests per day)

**Save the API key** - it looks like: `urt_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

### 2. Start the API Server

```bash
.\venv\Scripts\python.exe api_server.py
```

The server will start on `http://localhost:5000`

## API Endpoints

### Authentication
All endpoints (except `/api/health`) require an API key in the header:
```
X-API-Key: urt_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### Available Endpoints

#### 1. Health Check
```bash
GET /api/health
```
No authentication required.

#### 2. List Available Accounts
```bash
GET /api/accounts/available?website=unlocktool
```
Returns list of available accounts for rental.

#### 3. Rent an Account
```bash
POST /api/accounts/rent
Content-Type: application/json

{
  "website": "unlocktool",
  "customer_info": "Customer #12345"
}
```
Returns account credentials and expiry time.

#### 4. Return an Account
```bash
POST /api/accounts/return/1
```
Marks account as available before expiry.

#### 5. Check Account Status
```bash
GET /api/accounts/status/1
```
Check if account is available, rented, or expired.

#### 6. View Your Statistics
```bash
GET /api/stats/me?days=30
```
See your API usage statistics.

## Usage Examples

### Using cURL

**List available accounts:**
```bash
curl -H "X-API-Key: urt_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx" http://localhost:5000/api/accounts/available?website=unlocktool
```

**Rent an account:**
```bash
curl -X POST -H "X-API-Key: urt_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx" -H "Content-Type: application/json" -d "{\"website\":\"unlocktool\",\"customer_info\":\"John Doe\"}" http://localhost:5000/api/accounts/rent
```

### Using Python

```python
import requests

API_KEY = "urt_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
BASE_URL = "http://localhost:5000/api"

headers = {"X-API-Key": API_KEY}

# List available accounts
response = requests.get(f"{BASE_URL}/accounts/available?website=unlocktool", headers=headers)
print(response.json())

# Rent an account
data = {
    "website": "unlocktool",
    "customer_info": "Customer Portal"
}
response = requests.post(f"{BASE_URL}/accounts/rent", json=data, headers=headers)
account = response.json()
print(f"Username: {account['account']['username']}")
print(f"Password: {account['account']['password']}")
print(f"Expires: {account['account']['expires_at']}")
```

## Managing API Keys

Use `manage_api_keys.py` to:
1. **Create** new API keys
2. **List** all API keys
3. **View details** of specific API key usage
4. **Revoke** API keys
5. **View statistics** across all keys
6. **Monitor activity** in real-time

## Database Tables

The system creates these new tables:

### `api_keys`
- id, api_key_hash, name, email, status
- rate_limit, total_requests, created_at, last_used

### `api_usage`
- id, api_key_id, account_id, website
- action, ip_address, timestamp, response_status

## Workflow

1. **Customer requests account:**
   - API call to `/api/accounts/rent`
   - System finds available account
   - Returns credentials with expiry time

2. **Automatic expiry:**
   - After validity period (6h for unlocktool)
   - Account automatically marked as available
   - Password gets reset in next scheduled run

3. **Usage tracking:**
   - Every API request logged
   - Track which API key used which account
   - Monitor request counts and patterns

## Security Notes

- **API keys** are hashed in database
- **Never expose** API keys publicly
- **Rate limits** prevent abuse
- **Revoke** compromised keys immediately
- **Monitor** usage regularly

## Next Steps

1. Create your first API key
2. Start the API server
3. Test with cURL or Python
4. Integrate with your customer portal
5. Monitor usage via `manage_api_keys.py`
