-- VELOX-N8N Database Initialization Script
-- This script creates the initial database schema for the trading system

-- Create main application database
CREATE DATABASE velo_trading_dev;
CREATE DATABASE n8n_dev;
CREATE DATABASE openalgo_dev;

-- Connect to main database
\c velo_trading_dev;

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "btree_gin";

-- Create user roles
CREATE ROLE velo_read;
CREATE ROLE velo_write;
CREATE ROLE velo_admin;

-- Grant permissions
GRANT velo_read TO velo_read;
GRANT velo_write TO velo_write;
GRANT velo_admin TO velo_admin;

-- Users Table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    uuid UUID DEFAULT uuid_generate_v4() UNIQUE NOT NULL,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'investor',
    is_active BOOLEAN DEFAULT true,
    is_verified BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP WITH TIME ZONE,
    login_count INTEGER DEFAULT 0,
    failed_login_attempts INTEGER DEFAULT 0,
    locked_until TIMESTAMP WITH TIME ZONE
);

-- Strategies Table
CREATE TABLE IF NOT EXISTS strategies (
    id SERIAL PRIMARY KEY,
    uuid UUID DEFAULT uuid_generate_v4() UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    type VARCHAR(50) NOT NULL, -- 'trend', 'mean_reversion', 'momentum'
    config JSONB NOT NULL,
    n8n_workflow_id VARCHAR(100),
    n8n_workflow_json JSONB,
    is_active BOOLEAN DEFAULT false,
    is_paper_trading BOOLEAN DEFAULT true,
    created_by INTEGER REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_executed TIMESTAMP WITH TIME ZONE,
    execution_count INTEGER DEFAULT 0
);

-- Symbols Table
CREATE TABLE IF NOT EXISTS symbols (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    exchange VARCHAR(10) NOT NULL,
    sector VARCHAR(50),
    industry VARCHAR(50),
    market_cap BIGINT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Trades Table
CREATE TABLE IF NOT EXISTS trades (
    id SERIAL PRIMARY KEY,
    uuid UUID DEFAULT uuid_generate_v4() UNIQUE NOT NULL,
    strategy_id INTEGER REFERENCES strategies(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    symbol VARCHAR(20) NOT NULL,
    exchange VARCHAR(10) NOT NULL,
    side VARCHAR(10) NOT NULL CHECK (side IN ('BUY', 'SELL')),
    quantity INTEGER NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    executed_price DECIMAL(10, 2),
    status VARCHAR(20) NOT NULL DEFAULT 'PENDING' CHECK (status IN ('PENDING', 'EXECUTED', 'CANCELLED', 'REJECTED', 'PARTIAL')),
    order_type VARCHAR(20) NOT NULL DEFAULT 'MARKET' CHECK (order_type IN ('MARKET', 'LIMIT', 'STOP', 'STOP_LIMIT')),
    order_id VARCHAR(100),
    broker_order_id VARCHAR(100),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    executed_at TIMESTAMP WITH TIME ZONE,
    commission DECIMAL(10, 2) DEFAULT 0,
    taxes DECIMAL(10, 2) DEFAULT 0,
    slippage DECIMAL(10, 4) DEFAULT 0,
    notes TEXT,
    metadata JSONB
);

-- Positions Table
CREATE TABLE IF NOT EXISTS positions (
    id SERIAL PRIMARY KEY,
    uuid UUID DEFAULT uuid_generate_v4() UNIQUE NOT NULL,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    symbol VARCHAR(20) NOT NULL,
    exchange VARCHAR(10) NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 0,
    average_price DECIMAL(10, 2),
    current_price DECIMAL(10, 2),
    unrealized_pnl DECIMAL(12, 2) DEFAULT 0,
    realized_pnl DECIMAL(12, 2) DEFAULT 0,
    total_pnl DECIMAL(12, 2) DEFAULT 0,
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB
);

-- Market Data Table
CREATE TABLE IF NOT EXISTS market_data (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    exchange VARCHAR(10) NOT NULL,
    timeframe VARCHAR(10) NOT NULL, -- '1m', '5m', '15m', '30m', '1h', '4h', '1d'
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    open DECIMAL(10, 2) NOT NULL,
    high DECIMAL(10, 2) NOT NULL,
    low DECIMAL(10, 2) NOT NULL,
    close DECIMAL(10, 2) NOT NULL,
    volume BIGINT NOT NULL DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(symbol, exchange, timeframe, timestamp)
);

-- Indicator Data Table
CREATE TABLE IF NOT EXISTS indicator_data (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    exchange VARCHAR(10) NOT NULL,
    timeframe VARCHAR(10) NOT NULL,
    indicator_name VARCHAR(50) NOT NULL,
    indicator_params JSONB,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    value DECIMAL(15, 6) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(symbol, exchange, timeframe, indicator_name, indicator_params, timestamp)
);

-- Strategy Performance Table
CREATE TABLE IF NOT EXISTS strategy_performance (
    id SERIAL PRIMARY KEY,
    strategy_id INTEGER REFERENCES strategies(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    total_trades INTEGER DEFAULT 0,
    winning_trades INTEGER DEFAULT 0,
    losing_trades INTEGER DEFAULT 0,
    win_rate DECIMAL(5, 2) DEFAULT 0,
    total_pnl DECIMAL(12, 2) DEFAULT 0,
    max_drawdown DECIMAL(12, 2) DEFAULT 0,
    sharpe_ratio DECIMAL(8, 4) DEFAULT 0,
    sortino_ratio DECIMAL(8, 4) DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(strategy_id, date)
);

-- Risk Settings Table
CREATE TABLE IF NOT EXISTS risk_settings (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    max_position_size DECIMAL(12, 2) DEFAULT 100000,
    max_daily_loss DECIMAL(12, 2) DEFAULT 10000,
    max_open_positions INTEGER DEFAULT 10,
    risk_per_trade DECIMAL(5, 2) DEFAULT 2.0,
    max_correlation DECIMAL(5, 2) DEFAULT 0.7,
    stop_loss_method VARCHAR(20) DEFAULT 'atr_based',
    take_profit_method VARCHAR(20) DEFAULT 'fixed_risk_reward',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id)
);

-- Audit Log Table
CREATE TABLE IF NOT EXISTS audit_log (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(50) NOT NULL,
    resource_type VARCHAR(50) NOT NULL,
    resource_id VARCHAR(100),
    old_values JSONB,
    new_values JSONB,
    ip_address INET,
    user_agent TEXT,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    session_id VARCHAR(100)
);

-- System Settings Table
CREATE TABLE IF NOT EXISTS system_settings (
    id SERIAL PRIMARY KEY,
    key VARCHAR(100) UNIQUE NOT NULL,
    value TEXT,
    description TEXT,
    is_encrypted BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_uuid ON users(uuid);
CREATE INDEX IF NOT EXISTS idx_strategies_user_id ON strategies(created_by);
CREATE INDEX IF NOT EXISTS idx_strategies_type ON strategies(type);
CREATE INDEX IF NOT EXISTS idx_strategies_active ON strategies(is_active);
CREATE INDEX IF NOT EXISTS idx_trades_user_id ON trades(user_id);
CREATE INDEX IF NOT EXISTS idx_trades_strategy_id ON trades(strategy_id);
CREATE INDEX IF NOT EXISTS idx_trades_symbol ON trades(symbol);
CREATE INDEX IF NOT EXISTS idx_trades_timestamp ON trades(timestamp);
CREATE INDEX IF NOT EXISTS idx_trades_status ON trades(status);
CREATE INDEX IF NOT EXISTS idx_positions_user_id ON positions(user_id);
CREATE INDEX IF NOT EXISTS idx_positions_symbol ON positions(symbol);
CREATE INDEX IF NOT EXISTS idx_market_data_symbol ON market_data(symbol);
CREATE INDEX IF NOT EXISTS idx_market_data_timestamp ON market_data(timestamp);
CREATE INDEX IF NOT EXISTS idx_market_data_symbol_timeframe ON market_data(symbol, timeframe);
CREATE INDEX IF NOT EXISTS idx_indicator_data_symbol ON indicator_data(symbol);
CREATE INDEX IF NOT EXISTS idx_indicator_data_timestamp ON indicator_data(timestamp);
CREATE INDEX IF NOT EXISTS idx_audit_log_user_id ON audit_log(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_log_timestamp ON audit_log(timestamp);

-- Create triggers for updated_at columns
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_strategies_updated_at BEFORE UPDATE ON strategies
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_positions_updated_at BEFORE UPDATE ON positions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_risk_settings_updated_at BEFORE UPDATE ON risk_settings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_system_settings_updated_at BEFORE UPDATE ON system_settings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert default system settings
INSERT INTO system_settings (key, value, description) VALUES
('app_version', '1.0.0', 'Application version'),
('maintenance_mode', 'false', 'Maintenance mode flag'),
('max_api_requests_per_minute', '1000', 'API rate limit per minute'),
('session_timeout_minutes', '30', 'Session timeout in minutes'),
('default_timezone', 'Asia/Kolkata', 'Default timezone for the application'),
('market_open_time', '09:15', 'Market opening time'),
('market_close_time', '15:30', 'Market closing time'),
('trading_days', 'MONDAY,TUESDAY,WEDNESDAY,THURSDAY,FRIDAY', 'Trading days of week')
ON CONFLICT (key) DO NOTHING;

-- Insert default symbols (Indian market examples)
INSERT INTO symbols (symbol, name, exchange, sector, industry) VALUES
('NIFTY 50', 'Nifty 50 Index', 'NSE', 'Index', 'Broad Market'),
('BANKNIFTY', 'Nifty Bank Index', 'NSE', 'Index', 'Banking'),
('RELIANCE', 'Reliance Industries Ltd', 'NSE', 'Energy', 'Oil & Gas'),
('TCS', 'Tata Consultancy Services', 'NSE', 'Technology', 'IT Services'),
('HDFCBANK', 'HDFC Bank Ltd', 'NSE', 'Financial', 'Banking'),
('INFY', 'Infosys Ltd', 'NSE', 'Technology', 'IT Services'),
('ICICIBANK', 'ICICI Bank Ltd', 'NSE', 'Financial', 'Banking'),
('HINDUNILVR', 'Hindustan Unilever Ltd', 'NSE', 'Consumer Goods', 'FMCG'),
('SBIN', 'State Bank of India', 'NSE', 'Financial', 'Banking'),
('BHARTIARTL', 'Bharti Airtel Ltd', 'NSE', 'Telecom', 'Telecommunications')
ON CONFLICT (symbol) DO NOTHING;

-- Create read-only user for monitoring
CREATE USER velo_monitor WITH PASSWORD 'monitor_password_123';
GRANT CONNECT ON DATABASE velo_trading_dev TO velo_monitor;
GRANT USAGE ON SCHEMA public TO velo_monitor;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO velo_monitor;
GRANT SELECT ON ALL SEQUENCES IN SCHEMA public TO velo_monitor;

-- Create application user
CREATE USER velo_app WITH PASSWORD 'app_password_123';
GRANT CONNECT ON DATABASE velo_trading_dev TO velo_app;
GRANT USAGE ON SCHEMA public TO velo_app;
GRANT velo_read TO velo_app;
GRANT velo_write TO velo_app;

-- Output initialization complete message
DO $$
BEGIN
    RAISE NOTICE 'VELOX-N8N database initialization completed successfully';
END $$;