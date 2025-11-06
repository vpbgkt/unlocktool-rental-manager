# API Management System - Complete Setup

## ✅ What's Been Created

### 1. **API Manager** (`src/api_manager.py`)
- Generate and manage API keys
- Validate API keys with hashing
- Track usage statistics
- Log all API requests
- Rate limiting support

### 2. **REST API Server** (`api_server.py`)
- Flask-based REST API
- Authentication with API keys
- Account rental endpoints
- Usage statistics
- Auto-expiry management

### 3. **Management Tools**
- `manage_api_keys.py` - CLI for API key management
- `setup_api.py` - Quick setup script
- `test_api_client.py` - Python client example

### 4. **Database Tables**
- `api_keys` - Stores API keys (hashed)
- `api_usage` - Logs every API request

## 🚀 Quick Start

### Step 1: Your API Key
```
API Key: urt_74O0lEd-kHWsM_oD8-ngz6uUiluJtha05gru1L_rwFY
Name: Demo Customer Portal
Rate Limit: 100 requests/day
```

### Step 2: Start API Server
Open a NEW terminal and run:
```bash
.\venv\Scripts\python.exe api_server.py
```

This starts the server on `http://localhost:5000`

### Step 3: Test the API
In another terminal:
```bash
.\venv\Scripts\python.exe test_api_client.py
```

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check (no auth) |
| GET | `/api/accounts/available` | List available accounts |
| POST | `/api/accounts/rent` | Rent an account |
| POST | `/api/accounts/return/<id>` | Return an account |
| GET | `/api/accounts/status/<id>` | Check account status |
| GET | `/api/stats/me` | Your usage statistics |

## 🔑 Authentication

All endpoints (except health) require API key in header:
```
X-API-Key: urt_74O0lEd-kHWsM_oD8-ngz6uUiluJtha05gru1L_rwFY
```

## 💡 Use Cases

### 1. **Customer Portal**
Integrate the API into your website so customers can:
- Check available accounts
- Rent accounts automatically
- View expiry times

### 2. **Mobile App**
Build a mobile app that uses the API to:
- Browse available tools
- Rent accounts on-demand
- Track rental history

### 3. **Reseller System**
Give API keys to resellers who can:
- Rent accounts for their customers
- Track their usage
- Have their own rate limits

### 4. **Automated Systems**
Automate account distribution:
- Auto-rent on payment
- Auto-return on expiry
- Integration with payment gateways

## 📊 Tracking & Monitoring

### View All API Keys
```bash
.\venv\Scripts\python.exe manage_api_keys.py
# Choose option 2
```

### View Usage Statistics
```bash
.\venv\Scripts\python.exe manage_api_keys.py
# Choose option 5
```

### View Recent Activity
```bash
.\venv\Scripts\python.exe manage_api_keys.py
# Choose option 6
```

## 🔐 Security Features

1. **API Key Hashing**: Keys are hashed in database (SHA-256)
2. **Rate Limiting**: Prevent abuse (configurable per key)
3. **Request Logging**: Track every API call (IP, user agent)
4. **Key Revocation**: Instantly disable compromised keys
5. **Status Tracking**: Monitor API key usage in real-time

## 📈 Current System Status

✅ **Available Accounts**: 2
- vpbgkt (unlocktool)
- rameshkumawat (unlocktool)

✅ **Websites**: 2
- unlocktool (6 hours validity)
- androidmultitool (2 hours validity)

✅ **API Keys**: 1 active
- Demo Customer Portal (100 req/day)

## 🎯 Workflow Example

### Customer Rents Account:

1. **Customer calls API**:
```python
POST /api/accounts/rent
{
  "website": "unlocktool",
  "customer_info": "Customer #12345"
}
```

2. **API Response**:
```json
{
  "success": true,
  "account": {
    "username": "vpbgkt",
    "password": "2iapqDFT26OR5N-j",
    "expires_at": "2025-11-05 20:33:45",
    "validity_hours": 6
  }
}
```

3. **System tracks**:
- API key used
- Account rented
- Expiry time calculated
- Request logged

4. **Auto-expiry**:
- After 6 hours, account becomes available
- Next password reset updates credentials
- Account ready for next rental

## 🛠️ Advanced Usage

### Create Additional API Keys
```bash
.\venv\Scripts\python.exe manage_api_keys.py
# Choose option 1
```

### Monitor Specific API Key
```bash
.\venv\Scripts\python.exe manage_api_keys.py
# Choose option 3, enter API Key ID
```

### Revoke Compromised Key
```bash
.\venv\Scripts\python.exe manage_api_keys.py
# Choose option 4, confirm revocation
```

## 📝 Integration Example

### JavaScript (Fetch)
```javascript
const API_KEY = 'urt_74O0lEd-kHWsM_oD8-ngz6uUiluJtha05gru1L_rwFY';

fetch('http://localhost:5000/api/accounts/rent', {
  method: 'POST',
  headers: {
    'X-API-Key': API_KEY,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    website: 'unlocktool',
    customer_info: 'Web Portal Customer'
  })
})
.then(res => res.json())
.then(data => {
  console.log('Account:', data.account.username);
  console.log('Password:', data.account.password);
  console.log('Expires:', data.account.expires_at);
});
```

### PHP
```php
<?php
$api_key = 'urt_74O0lEd-kHWsM_oD8-ngz6uUiluJtha05gru1L_rwFY';

$ch = curl_init('http://localhost:5000/api/accounts/rent');
curl_setopt($ch, CURLOPT_POST, 1);
curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode([
    'website' => 'unlocktool',
    'customer_info' => 'PHP Customer'
]));
curl_setopt($ch, CURLOPT_HTTPHEADER, [
    'X-API-Key: ' . $api_key,
    'Content-Type: application/json'
]);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);

$response = curl_exec($ch);
$data = json_decode($response, true);

echo "Username: " . $data['account']['username'] . "\n";
echo "Password: " . $data['account']['password'] . "\n";
?>
```

## 🎉 You're Ready!

Your complete tool rental API system is now set up with:
- ✅ API key management
- ✅ Account rental system
- ✅ Usage tracking
- ✅ Auto-expiry
- ✅ Security features
- ✅ Client examples

**Next**: Start the server and test with the Python client!
