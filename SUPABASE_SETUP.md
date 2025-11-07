# Supabase Setup Guide

## Step 1: Create Supabase Account

1. Go to https://supabase.com
2. Click "Start your project"
3. Sign up with GitHub (recommended) or email
4. Create a new project:
   - Project Name: `unlocktool-rental`
   - Database Password: (create a strong password - SAVE THIS!)
   - Region: Choose closest to you (e.g., US East)
5. Wait 2-3 minutes for project to initialize

## Step 2: Get Your Credentials

Once project is ready, go to Project Settings → API:

```
Project URL: https://xxxxx.supabase.co
Project API Key (anon/public): eyJhbGc...
Service Role Key: eyJhbGc...
```

**SAVE THESE - You'll need them!**

## Step 3: Run Database Migration

1. In Supabase Dashboard, go to SQL Editor
2. Click "New Query"
3. Copy the SQL from `supabase_schema.sql` (created below)
4. Click "Run" to execute

## Step 4: Configure Local Bot

Update `config/supabase_config.json` with your credentials:
```json
{
  "url": "https://xxxxx.supabase.co",
  "anon_key": "your-anon-key-here",
  "service_key": "your-service-role-key-here"
}
```

## Step 5: Test Connection

```bash
python test_supabase.py
```

If you see "✓ Connected to Supabase!" - you're ready!

## What You Get FREE Forever:

✅ 500MB PostgreSQL Database
✅ Unlimited API Requests
✅ Real-time subscriptions
✅ Auto-generated REST API
✅ Row Level Security
✅ Automatic backups

## Next Steps:

After setup, your system will:
1. Run Selenium bot locally (on your PC)
2. Store/retrieve data from Supabase (cloud)
3. Serve API to customers (from Supabase)
4. Sync everything in real-time

Let's get started! 🚀
