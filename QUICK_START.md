# 🚀 Quick Start - Hybrid Mode

## ✅ What You Have Now

**Hybrid System = Local Automation + Cloud Database**

- 🖥️ Selenium runs on YOUR PC (free reCAPTCHA)
- ☁️ Data syncs to Supabase cloud (free database)
- 🌐 Customers access via API (real-time data)
- 💰 **Total Cost: $0/month**

---

## 🎯 Common Commands

### Test Everything:
```bash
python test_hybrid_mode.py
```

### Run Password Reset (with cloud sync):
```bash
python main.py --mode run-once
```
**You'll solve reCAPTCHA, then bot does the rest + syncs to cloud!**

### Start API Server:
```bash
python api_server.py
```
**Should show:** `✓ Using Supabase cloud database`

### Test API:
```bash
curl http://localhost:5000/api/accounts/available?website=unlocktool \
  -H "X-API-Key: urt_74O0lEd-kHWsM_oD8-ngz6uUiluJtha05gru1L_rwFY"
```

---

## 📊 Check Status

### View Supabase Data:
1. Go to: https://supabase.com/dashboard
2. Click **Table Editor**
3. Browse: `accounts`, `password_history`, `rentals`

### Get Statistics:
```bash
python -c "from src.supabase_db import SupabaseDB; db = SupabaseDB(); print(db.get_dashboard_stats())"
```

### View Logs:
```bash
# Latest password reset log
cat logs/password_reset_*.log | tail -20
```

---

## 🔧 Key Files Modified

| File | What Changed |
|------|--------------|
| `src/scheduler.py` | Added cloud sync after password resets |
| `api_server.py` | Uses Supabase as primary database |
| `test_hybrid_mode.py` | NEW - Verify hybrid mode setup |
| `HYBRID_MODE_READY.md` | NEW - Complete documentation |

---

## ✅ What to Look For

### Successful Password Reset with Cloud Sync:
```
INFO: Password reset successful for vpbgkt
INFO: ✓ Password synced to Supabase cloud for vpbgkt  ← LOOK FOR THIS!
INFO: ✓ New password saved to local database and config
```

### API Using Cloud Database:
```
✓ Using Supabase cloud database  ← LOOK FOR THIS!

Tool Rental API Server
==========================================
```

### API Response Shows Cloud:
```json
{
  "success": true,
  "database": "Supabase",  ← LOOK FOR THIS!
  "accounts": [...]
}
```

---

## 🎊 You're Ready!

**Three simple steps:**

1. **Test:** `python test_hybrid_mode.py`
2. **Run:** `python main.py --mode run-once`
3. **Verify:** Check Supabase dashboard

**All documentation:**
- `HYBRID_MODE_READY.md` - Complete setup guide
- `IMPLEMENTATION_COMPLETE.md` - What was done
- `SUPABASE_SETUP.md` - Supabase configuration

**Happy automating!** 🚀
