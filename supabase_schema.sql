-- Supabase Database Schema for Tool Rental System
-- Run this in Supabase SQL Editor

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Websites/Tools Table
CREATE TABLE IF NOT EXISTS websites (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    url TEXT NOT NULL,
    validity_hours INTEGER NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Accounts Table
CREATE TABLE IF NOT EXISTS accounts (
    id SERIAL PRIMARY KEY,
    website_id INTEGER NOT NULL REFERENCES websites(id) ON DELETE CASCADE,
    username TEXT NOT NULL,
    email TEXT,
    current_password TEXT NOT NULL,
    status TEXT DEFAULT 'available' CHECK (status IN ('available', 'rented', 'exception')),
    rented_at TIMESTAMP WITH TIME ZONE,
    available_at TIMESTAMP WITH TIME ZONE,
    last_reset TIMESTAMP WITH TIME ZONE,
    failed_login_attempts INTEGER DEFAULT 0,
    last_failed_login TIMESTAMP WITH TIME ZONE,
    exception_reason TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(website_id, username)
);

-- Password History Table
CREATE TABLE IF NOT EXISTS password_history (
    id SERIAL PRIMARY KEY,
    account_id INTEGER NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
    old_password TEXT,
    new_password TEXT NOT NULL,
    reset_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    status TEXT NOT NULL,
    message TEXT
);

-- Rentals Table
CREATE TABLE IF NOT EXISTS rentals (
    id SERIAL PRIMARY KEY,
    account_id INTEGER NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
    customer_name TEXT,
    customer_email TEXT,
    customer_phone TEXT,
    rented_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    returned_at TIMESTAMP WITH TIME ZONE,
    status TEXT DEFAULT 'active' CHECK (status IN ('active', 'completed', 'expired'))
);

-- API Keys Table
CREATE TABLE IF NOT EXISTS api_keys (
    id SERIAL PRIMARY KEY,
    key TEXT UNIQUE NOT NULL,
    key_hash TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    email TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    rate_limit INTEGER DEFAULT 100,
    total_requests INTEGER DEFAULT 0,
    last_used TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- API Usage Logs Table
CREATE TABLE IF NOT EXISTS api_usage_logs (
    id SERIAL PRIMARY KEY,
    api_key_id INTEGER REFERENCES api_keys(id) ON DELETE SET NULL,
    action TEXT NOT NULL,
    website TEXT,
    account_id INTEGER REFERENCES accounts(id) ON DELETE SET NULL,
    ip_address TEXT,
    user_agent TEXT,
    response_status TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create Indexes for Performance
CREATE INDEX IF NOT EXISTS idx_accounts_status ON accounts(status);
CREATE INDEX IF NOT EXISTS idx_accounts_website ON accounts(website_id);
CREATE INDEX IF NOT EXISTS idx_accounts_available_at ON accounts(available_at);
CREATE INDEX IF NOT EXISTS idx_rentals_status ON rentals(status);
CREATE INDEX IF NOT EXISTS idx_rentals_expires ON rentals(expires_at);
CREATE INDEX IF NOT EXISTS idx_password_history_account ON password_history(account_id);
CREATE INDEX IF NOT EXISTS idx_api_usage_api_key ON api_usage_logs(api_key_id);
CREATE INDEX IF NOT EXISTS idx_api_usage_created ON api_usage_logs(created_at);

-- Insert Initial Websites
INSERT INTO websites (name, url, validity_hours, description) VALUES
    ('unlocktool', 'https://unlocktool.net', 6, 'Unlock Tool - 6 hours validity'),
    ('androidmultitool', 'https://androidmultitool.com', 2, 'Android Multi Tool - 2 hours validity')
ON CONFLICT (name) DO NOTHING;

-- Function to Auto-Expire Rentals
CREATE OR REPLACE FUNCTION auto_expire_rentals()
RETURNS void AS $$
BEGIN
    -- Mark accounts as available if rental expired
    UPDATE accounts 
    SET status = 'available', 
        available_at = CURRENT_TIMESTAMP
    WHERE id IN (
        SELECT account_id FROM rentals 
        WHERE status = 'active' 
        AND expires_at < CURRENT_TIMESTAMP
    );
    
    -- Mark expired rentals as expired
    UPDATE rentals 
    SET status = 'expired'
    WHERE status = 'active' 
    AND expires_at < CURRENT_TIMESTAMP;
END;
$$ LANGUAGE plpgsql;

-- Function to Get Available Accounts (with auto-expiry)
CREATE OR REPLACE FUNCTION get_available_accounts(website_name TEXT)
RETURNS TABLE (
    id INTEGER,
    username TEXT,
    email TEXT,
    current_password TEXT,
    last_reset TIMESTAMP WITH TIME ZONE,
    validity_hours INTEGER
) AS $$
BEGIN
    -- First expire old rentals
    PERFORM auto_expire_rentals();
    
    -- Return available accounts
    RETURN QUERY
    SELECT 
        a.id,
        a.username,
        a.email,
        a.current_password,
        a.last_reset,
        w.validity_hours
    FROM accounts a
    JOIN websites w ON a.website_id = w.id
    WHERE w.name = website_name 
    AND a.status = 'available'
    ORDER BY a.last_reset ASC NULLS FIRST;
END;
$$ LANGUAGE plpgsql;

-- Enable Row Level Security (RLS)
ALTER TABLE websites ENABLE ROW LEVEL SECURITY;
ALTER TABLE accounts ENABLE ROW LEVEL SECURITY;
ALTER TABLE password_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE rentals ENABLE ROW LEVEL SECURITY;
ALTER TABLE api_keys ENABLE ROW LEVEL SECURITY;
ALTER TABLE api_usage_logs ENABLE ROW LEVEL SECURITY;

-- Create Policies for Public API Access
-- (Allow service role to do everything, anon key has limited access)

-- Websites: Public read
CREATE POLICY "Allow public read access to websites"
    ON websites FOR SELECT
    USING (true);

-- Accounts: Service role only
CREATE POLICY "Allow service role full access to accounts"
    ON accounts FOR ALL
    USING (auth.role() = 'service_role');

-- Password History: Service role only
CREATE POLICY "Allow service role full access to password_history"
    ON password_history FOR ALL
    USING (auth.role() = 'service_role');

-- Rentals: Service role only
CREATE POLICY "Allow service role full access to rentals"
    ON rentals FOR ALL
    USING (auth.role() = 'service_role');

-- API Keys: Service role only
CREATE POLICY "Allow service role full access to api_keys"
    ON api_keys FOR ALL
    USING (auth.role() = 'service_role');

-- API Usage Logs: Service role only
CREATE POLICY "Allow service role full access to api_usage_logs"
    ON api_usage_logs FOR ALL
    USING (auth.role() = 'service_role');

-- Success message
DO $$
BEGIN
    RAISE NOTICE '✓ Database schema created successfully!';
    RAISE NOTICE '✓ Initial websites added (unlocktool, androidmultitool)';
    RAISE NOTICE '✓ Auto-expiry function enabled';
    RAISE NOTICE '✓ Row Level Security configured';
    RAISE NOTICE '';
    RAISE NOTICE 'Next steps:';
    RAISE NOTICE '1. Add your accounts using the API or SQL';
    RAISE NOTICE '2. Generate API keys for customers';
    RAISE NOTICE '3. Configure local bot with Supabase credentials';
END $$;
