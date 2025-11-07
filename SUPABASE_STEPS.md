# 🚀 Supabase Setup - Step by Step

## Current Status: ✅ Supabase Client Installed

You now have all the files needed! Follow these steps:

---

## Step 1: Create Supabase Account (5 minutes)

1. **Open Browser**: Go to https://supabase.com
2. **Sign Up**: Click "Start your project" → Sign up with GitHub (recommended)
3. **Create Project**:
   - Click "New Project"
   - Organization: Create new or use existing
   - Project Name: `unlocktool-rental`
   - Database Password: Create a **STRONG** password (save it!)
   - Region: Choose closest to you (US East, EU West, etc.)
   - Click "Create new project"
4. **Wait**: Takes 2-3 minutes for project to initialize

---

## Step 2: Get Your API Credentials (1 minute)

1. **In Supabase Dashboard**, go to: **Project Settings** (gear icon) → **API**
2. **Copy these values**:
   ```
   Project URL: https://xxxxx.supabase.co
   Project API Key (anon, public): eyJhbGc...
   Service Role Key: eyJhbGc...
   ```

3. **Update config file**: Open `config/supabase_config.json` and paste:
   ```json
   {
     "url": "https://xxxxx.supabase.co",
     "anon_key": "paste-anon-key-here",
     "service_key": "paste-service-role-key-here"
   }
   ```

---

## Step 3: Run Database Schema (2 minutes)

1. **In Supabase Dashboard**, go to: **SQL Editor** (left sidebar)
2. **Click**: "New Query"
3. **Open file**: `supabase_schema.sql` (in your project folder)
4. **Copy all SQL** from that file
5. **Paste** into SQL Editor
6. **Click "Run"** (bottom right)
7. **Wait** for success message: "Success. No rows returned"

You should see output like:
```
✓ Database schema created successfully!
✓ Initial websites added (unlocktool, androidmultitool)
✓ Auto-expiry function enabled
✓ Row Level Security configured
```

---

## Step 4: Migrate Your Existing Accounts (3 minutes)

Run this command to copy accounts from local SQLite to Supabase:

```bash
.\venv\Scripts\python.exe migrate_to_supabase.py
```

This will:
- ✅ Connect to your local database
- ✅ Upload all accounts to Supabase
- ✅ Upload password history
- ✅ Verify everything transferred

---

## Step 5: Test Connection (1 minute)

```bash
.\venv\Scripts\python.exe test_supabase.py
```

You should see:
```
✓ Connected successfully!
✓ Found 2 websites
✓ Found 2 accounts
✓ All tests passed! Supabase is ready to use!
```

---

## Step 6: Update Your System to Use Supabase

**Option A: Switch Completely to Supabase**
I'll update all your scripts to use Supabase instead of SQLite.

**Option B: Hybrid Mode**
Keep SQLite locally, sync to Supabase for API access.

Which would you like? (Type 'A' or 'B')

---

## What You Get with Supabase:

✅ **FREE Forever**: 500MB PostgreSQL database
✅ **Global Access**: Access from anywhere with API
✅ **Auto-API**: REST API automatically generated
✅ **Real-time**: Live updates when data changes
✅ **Backups**: Automatic daily backups
✅ **Security**: Row-level security built-in
✅ **Dashboard**: Beautiful UI to view/edit data
✅ **No Limits**: Unlimited API requests

---

## Troubleshooting

### Can't connect?
- Check `config/supabase_config.json` has correct credentials
- Make sure you used `service_key` not `anon_key`
- Verify project is active in Supabase Dashboard

### Schema errors?
- Make sure you ran the ENTIRE `supabase_schema.sql` file
- Check SQL Editor for any error messages
- Try running schema again (it's safe to re-run)

### Test fails?
- Verify Supabase client installed: `pip list | grep supabase`
- Check internet connection
- Make sure project URL is correct (no typos)

---

## Ready to Start?

1. ✅ Create Supabase account
2. ✅ Get API credentials
3. ✅ Run database schema
4. ✅ Test connection
5. ✅ Migrate existing data
6. ✅ Start using cloud database!

**Let me know when you've completed Step 2 (got your API credentials) and I'll help with the rest!** 🚀
