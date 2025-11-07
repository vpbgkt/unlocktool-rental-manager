# 🚀 Hybrid Mode Activated!

## ✅ System Architecture

```
┌─────────────────────────────────────────────────────────┐
│          YOUR PC (Local - FREE reCAPTCHA Solving)        │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Selenium Bot (Chrome Visible)                   │   │
│  │  - YOU solve reCAPTCHA (5 seconds)              │   │
│  │  - Runs every 6 hours                            │   │
│  │  - Resets passwords                              │   │
│  └──────────────┬───────────────────────────────────┘   │
│                 │ After successful reset:                │
│                 │ 1. Save to SQLite (local backup)       │
│                 │ 2. Sync to Supabase (cloud) ✓          │
│                 │ 3. Update config file                  │
│                 ▼                                         │
└─────────────────────────────────────────────────────────┘
                  │
                  │ HTTPS Secure API Call
                  │
┌─────────────────▼───────────────────────────────────────┐
│       Supabase Cloud (FREE Forever - Real-time Data)     │
│  ┌──────────────────────────────────────────────────┐   │
│  │  PostgreSQL Database                             │   │
│  │  - Latest passwords                              │   │
│  │  - Rental tracking                               │   │
│  │  - Auto-expiry system                            │   │
│  └──────────────────────────────────────────────────┘   │
│                                                           │
│  📡 API Endpoints (Accessed by Customers):               │
│  - GET /api/accounts/available                           │
│  - POST /api/accounts/rent                               │
│  - POST /api/accounts/return/<id>                        │
│  - GET /api/accounts/status/<id>                         │
└─────────────────────────────────────────────────────────┘
```

---

## 🎯 How Password Reset Works

### Step-by-Step Process:

```bash
# Run password reset (manual or scheduled):
python main.py --mode run-once
```

**What Happens:**

1. **Chrome opens on YOUR screen** (visible browser)
2. **Bot navigates** to unlocktool.net
3. **Cloudflare bypass** (automatic)
4. **reCAPTCHA appears** → 👉 **YOU SOLVE IT** (takes 5 seconds)
5. **Bot logs in** with old password
6. **Bot resets** password
7. **Triple Save:**
   - ✅ Local SQLite database (backup)
   - ✅ **Supabase cloud** (real-time sync)
   - ✅ Config file updated

**Console Output:**
```
INFO: Starting password reset for vpbgkt
INFO: Cloudflare check passed
INFO: Login successful
INFO: Password reset successful for vpbgkt
INFO: ✓ Password synced to Supabase cloud for vpbgkt  ← NEW!
INFO: ✓ New password saved to local database and config
```

---

## 💰 Cost Comparison

| Approach | VPS | Captcha Solver | Database | Total |
|----------|-----|----------------|----------|-------|
| **Full Cloud** | $15/mo | $3/1000 solves | Included | **$20-30/mo** |
| **Hybrid Mode** ✅ | **$0** | **$0 (manual)** | **$0 (Supabase)** | **$0/mo** 🎉 |

**Your savings: $240-360 per year!**

---

## 🧪 Test Your System

### Test 1: Verify Supabase Connection

```bash
python test_supabase.py
```

**Expected:**
```
✓ Connected to Supabase: https://vzpbyhjgqchpdaedabru.supabase.co
✓ Found 2 websites
✓ Found 2 accounts
✓ All tests passed!
```

### Test 2: Run Password Reset with Cloud Sync

```bash
python main.py --mode run-once
```

**Look for this line:**
```
INFO: ✓ Password synced to Supabase cloud for <username>
```

### Test 3: Start API Server

```bash
python api_server.py
```

**Expected:**
```
✓ Using Supabase cloud database  ← Confirms cloud mode!

Tool Rental API Server
==========================================
Starting server on http://localhost:5000
```

### Test 4: Test API Endpoint

```bash
curl http://localhost:5000/api/accounts/available?website=unlocktool \
  -H "X-API-Key: urt_74O0lEd-kHWsM_oD8-ngz6uUiluJtha05gru1L_rwFY"
```

**Response should show:**
```json
{
  "success": true,
  "database": "Supabase",  ← Confirms cloud data!
  "accounts": [...]
}
```

---

## 🔄 Code Changes Made

### 1. `src/scheduler.py` - Added Cloud Sync

**New Code:**
```python
# Initialize Supabase
self.cloud_db = SupabaseDB()
self.logger.info("✓ Supabase cloud sync enabled")

# After successful password reset:
# 1. Save locally
self.db.update_password(account_id, old_pw, new_pw)

# 2. Sync to cloud
if self.cloud_db:
    self.cloud_db.update_password(account_id, old_pw, new_pw)
    self.logger.info(f"✓ Password synced to Supabase cloud")
```

### 2. `api_server.py` - Intelligent Database Selection

**New Code:**
```python
# Use Supabase as primary, SQLite as fallback
try:
    db = SupabaseDB()
    print("✓ Using Supabase cloud database")
except Exception as e:
    print(f"⚠ Supabase not available, falling back to SQLite")
    db = PasswordResetDB()
```

### 3. Exception Handling - Syncs to Both Databases

```python
# Mark in local database
self.db.mark_account_exception(account_id, 'wrong_password')

# Mark in Supabase
if self.cloud_db:
    self.cloud_db.mark_account_exception(account_id, 'wrong_password')
```

---

## 🗓️ Automation Setup

### Windows Task Scheduler:

1. Open Task Scheduler (`Win + R` → `taskschd.msc`)
2. Create Task:
   - **Name**: Unlocktool Password Reset
   - **Trigger**: Every 6 hours
   - **Action**: `python.exe main.py --mode run-once`
   - **Condition**: Only when user is logged on (so you can solve reCAPTCHA)

---

## 📊 Monitor Your System

### View Supabase Dashboard:
1. Go to: https://supabase.com/dashboard
2. Click **Table Editor**
3. View real-time data:
   - `accounts` - Current status
   - `password_history` - All changes
   - `rentals` - Active rentals

### Check Statistics:
```bash
python -c "from src.supabase_db import SupabaseDB; db = SupabaseDB(); print(db.get_dashboard_stats())"
```

---

## 🎉 Benefits of Hybrid Mode

| Feature | Value |
|---------|-------|
| **FREE reCAPTCHA** | You solve it manually (5 sec) |
| **No VPS costs** | Runs on your PC |
| **Cloud database** | Supabase (FREE forever) |
| **Access anywhere** | Via Supabase API |
| **Real-time sync** | Instant updates |
| **Auto-expiry** | Automatic rental management |
| **Easy debugging** | See browser on your screen |
| **Cloudflare works** | Better success rate locally |

---

## 🚨 Troubleshooting

### "Supabase not available" Error

**Check config:**
```bash
cat config/supabase_config.json
python test_supabase.py
```

### API shows "database": "SQLite"

**Restart API server:**
```bash
python api_server.py
```
Should see: `✓ Using Supabase cloud database`

### Password reset fails

**System automatically:**
- Marks account as exception
- Syncs to both databases
- Prevents customer rental

---

## ✅ Ready Checklist

- [x] Supabase database deployed
- [x] Data migrated (2 accounts, 6 history records)
- [x] Scheduler updated with cloud sync
- [x] API server using Supabase
- [x] Exception handling syncs to cloud
- [ ] Test password reset with Supabase sync
- [ ] Test API endpoints
- [ ] Set up Windows Task Scheduler

---

## 🚀 You're All Set!

Your system now runs in **HYBRID MODE**:
- ✅ Selenium on your PC (free reCAPTCHA)
- ✅ Database in Supabase (free cloud)
- ✅ API serves real-time cloud data
- ✅ **100% FREE** to operate!

**Start testing now:**
```bash
# Test connection
python test_supabase.py

# Run password reset
python main.py --mode run-once

# Start API
python api_server.py
```

**Happy automating!** 🎊
