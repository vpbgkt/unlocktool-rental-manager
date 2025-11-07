# 🎯 Smart Rental-Aware Password Reset System

## Overview

Your system now intelligently monitors active rentals and prioritizes password resets based on expiry times! This ensures accounts are always available when customers need them.

---

## 🆕 New Features

### 1. **Rental Expiry Checker**
- Automatically checks Supabase for active rentals
- Identifies accounts that will expire soon
- Prioritizes password resets by urgency

### 2. **Real-Time Dashboard**
- Shows all active rentals with countdown timers
- Color-coded urgency levels
- Suggests optimal reset times

### 3. **Smart Scheduling**
- Resets accounts with expiring rentals FIRST
- Then resets other accounts
- Minimizes downtime between rental and reset

### 4. **Live Monitoring Tool**
- Continuously displays rental status
- Updates every 30 seconds
- Shows exactly when to reset passwords

---

## 📋 Usage Examples

### Check Current Rental Status

```bash
# Quick status check
.\venv\Scripts\python.exe main.py --mode check-rentals
```

**Output Example:**
```
================================================================================
 📊 RENTAL STATUS DASHBOARD
================================================================================

⚠️  Found 1 active rental(s) to monitor:
--------------------------------------------------------------------------------

1. 🟠 HIGH - vpbgkt (unlocktool)
   Customer: John Doe
   Expires: 2025-11-07 03:30:00
   Time Remaining: 12 minutes
   ⏰ Reset password at: 03:25:00

--------------------------------------------------------------------------------

📈 Overall Statistics:
   Total Accounts: 2
   Available: 1
   Rented: 1
   Exceptions: 0

================================================================================
 Last updated: 2025-11-07 03:18:00
================================================================================
```

### Run Password Reset with Smart Prioritization

```bash
# System automatically prioritizes accounts by rental expiry
.\venv\Scripts\python.exe main.py --mode run-once
```

**Output Example:**
```
================================================================================
 📊 RENTAL STATUS DASHBOARD
================================================================================

⚠️  Found 1 active rental(s) to monitor:

1. 🔴 CRITICAL - vpbgkt (unlocktool)
   Time Remaining: 8 minutes
   ⏰ ACTION REQUIRED: Reset password NOW!

🔄 PASSWORD RESET ORDER:
   1. vpbgkt - Rental expiring soon  ← PRIORITY!
   2. rameshkumawat - Regular reset

Starting batch password reset...
```

### Real-Time Monitoring (Continuous)

```bash
# Monitor rentals with live countdown timers
.\venv\Scripts\python.exe monitor_rentals.py
```

**Features:**
- Updates every 30 seconds
- Shows countdown timers
- Color-coded urgency
- Tells you exactly when to reset

**Output Example:**
```
================================================================================
 📊 RENTAL DASHBOARD - 2025-11-07 03:18:45
================================================================================

 ⚠️  Active Rentals: 1
--------------------------------------------------------------------------------

 1. 🟠 HIGH vpbgkt @ unlocktool
    Customer: John Doe
    Email: john@example.com
    Expires: 2025-11-07 03:30:00
    ⏱️  Time Left: 11m
    📋 Action: Reset password soon
    ⏰ Reset at: 03:25:00

--------------------------------------------------------------------------------

📈 Overall Statistics:
    Total Accounts: 2
    Available: 1 🟢
    Rented: 1 🔵
    Exceptions: 0 🔴

================================================================================
 Next update in 30 seconds... (Press Ctrl+C to exit)
================================================================================
```

---

## 🎨 Urgency Levels

| Level | Icon | Time Remaining | Action |
|-------|------|----------------|--------|
| **CRITICAL** | 🔴 | ≤ 5 minutes | Reset password IMMEDIATELY! |
| **HIGH** | 🟠 | ≤ 15 minutes | Reset password soon |
| **MEDIUM** | 🟡 | ≤ 30 minutes | Monitor closely |
| **LOW** | 🟢 | > 30 minutes | No action needed |

---

## 🔄 How It Works

### Before Password Reset:

```
1. System connects to Supabase
2. Checks all active rentals
3. Calculates time remaining for each
4. Identifies accounts expiring soon (< 30 min)
5. Prioritizes reset order:
   - Accounts with expiring rentals FIRST
   - Other accounts SECOND
```

### Smart Reset Logic:

```python
# Example: 2 accounts configured

Account 1 (vpbgkt):
  - Currently rented
  - Expires in 12 minutes
  - Priority: 1 (URGENT - reset first!)

Account 2 (rameshkumawat):
  - Available
  - No rental
  - Priority: 2 (reset after vpbgkt)

Reset Order: vpbgkt → rameshkumawat
```

---

## 📊 API Integration

The rental checker works with your existing API:

```bash
# Customer rents account via API
curl -X POST http://localhost:5000/api/accounts/rent \
  -H "X-API-Key: urt_..." \
  -d '{"website": "unlocktool"}'

# Response:
{
  "success": true,
  "account": {
    "username": "vpbgkt",
    "expires_at": "2025-11-07 09:30:00"  ← System tracks this!
  }
}

# Your system now knows:
# - Account vpbgkt is rented
# - Expires at 09:30:00
# - Should reset password ~5 minutes before (09:25:00)
```

---

## 🕐 Recommended Workflow

### Option 1: Manual Monitoring

```bash
# 1. Check status before each reset
.\venv\Scripts\python.exe main.py --mode check-rentals

# 2. If urgent resets needed, run:
.\venv\Scripts\python.exe main.py --mode run-once
```

### Option 2: Continuous Monitoring

```bash
# Run monitor in one terminal
.\venv\Scripts\python.exe monitor_rentals.py

# When it shows "⏰ Reset at: HH:MM:SS", run in another terminal:
.\venv\Scripts\python.exe main.py --mode run-once
```

### Option 3: Scheduled with Pre-Check

```powershell
# Windows Task Scheduler script:
# 1. Check if any rentals expire in next 10 minutes
# 2. If yes, run password reset
# 3. If no, skip

# Save as: smart_reset.ps1
cd C:\Users\Vishal\Desktop\LocalWorkspace\unlocktoolauto
.\venv\Scripts\python.exe main.py --mode check-rentals
```

---

## 🎯 Benefits

### Before (Old System):
- ❌ Reset passwords blindly every X hours
- ❌ Might reset while customer is using account
- ❌ No visibility into rental status
- ❌ Customers might get expired accounts

### After (Smart System):
- ✅ Resets prioritized by rental expiry
- ✅ Visual dashboard shows all rentals
- ✅ Know exactly when to reset
- ✅ Minimize downtime between rental and reset
- ✅ Better customer experience

---

## 📈 Example Scenario

### Scenario: Multiple Rentals

```
Time: 03:00:00

Active Rentals:
  1. vpbgkt → Expires 03:30:00 (30 min) 🟡 MEDIUM
  2. account2 → Expires 04:00:00 (60 min) 🟢 LOW
  3. account3 → Expires 05:00:00 (120 min) 🟢 LOW

Recommendation: Reset vpbgkt at 03:25:00
```

```
Time: 03:25:00

Run: python main.py --mode run-once

Smart Reset Order:
  1. vpbgkt (expires soon - PRIORITY)
  2. account2 (regular reset)
  3. account3 (regular reset)

Result:
  ✅ vpbgkt: New password ready by 03:27:00
  ✅ Expires at 03:30:00
  ✅ 3 minutes buffer time
  ✅ Customer rental ends smoothly
  ✅ Account immediately available with new password
```

---

## 🛠️ Configuration

### Adjust Warning Time

Edit `src/scheduler.py`:

```python
# Check rentals expiring in next 60 minutes (default: 30)
expiring = self.check_rental_expiry(warning_minutes=60)
```

### Adjust Monitor Refresh Rate

```bash
# Update every 10 seconds (default: 30)
.\venv\Scripts\python.exe monitor_rentals.py --refresh 10
```

### Set Reset Buffer Time

```python
# Reset 10 minutes before expiry (default: 5)
'should_reset_now': minutes_remaining <= 10
```

---

## 🚨 Troubleshooting

### "No rentals expiring" but API shows active rental

**Check:**
```bash
# Verify Supabase has rental data
.\venv\Scripts\python.exe test_supabase.py
```

### Monitor not updating

**Solution:**
```bash
# Increase refresh rate
.\venv\Scripts\python.exe monitor_rentals.py --refresh 15
```

### Wrong priority order

**Check:**
```bash
# View current rental status
.\venv\Scripts\python.exe main.py --mode check-rentals
```

---

## 📝 Summary

### New Commands:

| Command | Purpose |
|---------|---------|
| `main.py --mode check-rentals` | Check rental status once |
| `monitor_rentals.py` | Live monitoring with countdown |
| `monitor_rentals.py --refresh 10` | Live monitor (10s refresh) |

### Key Features:

- ✅ Rental expiry detection
- ✅ Smart reset prioritization
- ✅ Real-time dashboard
- ✅ Countdown timers
- ✅ Urgency levels
- ✅ Automated recommendations

### Workflow:

```
1. Customer rents account → Supabase tracks expiry
2. Monitor shows countdown → You see when to reset
3. System prioritizes resets → Expiring accounts first
4. Password reset on time → Customer gets expired account + new password ready
5. Smooth transition! → No downtime
```

---

## 🎉 Result

**You now have complete control over account availability!**

- Know exactly when each account expires
- Reset passwords at optimal times
- Maximize account uptime
- Better customer experience
- Professional rental management

**Next:** Run the monitor to see it in action! 🚀

```bash
.\venv\Scripts\python.exe monitor_rentals.py
```
