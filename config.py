"""
Configuration file for Bitcoin Factor Analysis Tool

Modify these settings to customize the analysis behavior
"""

import json
from datetime import datetime, timedelta
from pathlib import Path

# ============================================================================
# DATA FETCHING CONFIGURATION
# ============================================================================

# Historical data period
START_DATE = '2022-01-01'           # Start date for analysis
END_DATE = None                     # None = today, or specify 'YYYY-MM-DD'

# Default date range if not specified
DEFAULT_LOOKBACK_DAYS = 730         # 2 years of history

# ============================================================================
# ANALYSIS CONFIGURATION
# ============================================================================

# Maximum number of factors to analyze per run
MAX_FACTORS_PER_RUN = 15

# Minimum number of data points required for analysis
MIN_DATA_POINTS = 20

# Rolling window size for rolling correlation (days)
ROLLING_WINDOW = 30

# Correlation threshold for "strong" correlation
STRONG_CORR_THRESHOLD = 0.5
MODERATE_CORR_THRESHOLD = 0.3

# P-value threshold for statistical significance
SIGNIFICANCE_LEVEL = 0.05

# ============================================================================
# OUTPUT CONFIGURATION
# ============================================================================

# Output directory for reports
OUTPUT_DIR = 'BTC_Factor_Reports'

# PDF page size ('letter' or 'A4')
PDF_PAGE_SIZE = 'letter'

# Chart DPI (higher = better quality, slower rendering)
CHART_DPI = 150

# Chart figure size (inches)
CHART_WIDTH = 16
CHART_HEIGHT = 12

# ============================================================================
# VISUALIZATION SETTINGS
# ============================================================================

# Seaborn style ('whitegrid', 'white', 'dark', 'darkgrid', 'ticks')
SEABORN_STYLE = 'whitegrid'

# Color scheme
COLORS = {
    'btc': '#1f77b4',           # Blue
    'factor': '#ff7f0e',        # Orange
    'positive': '#2ca02c',      # Green
    'negative': '#d62728',      # Red
    'neutral': '#808080',       # Gray
}

# ============================================================================
# FACTOR MAPPING - CUSTOMIZE YOUR FACTORS HERE
# ============================================================================

# Add or modify factor-to-ticker mappings
CUSTOM_FACTORS = {
    # Indices
    'S&P 500': '^GSPC',
    'NASDAQ 100': '^NDX',
    'Dow Jones Industrial Average': '^DJI',
    'Russell 2000': '^RUT',
    'Nikkei 225': '^N225',
    'Hang Seng': '^HSI',
    'DAX': '^GDAXI',
    'STOXX Europe 600': '^STOXX',
    
    # Bonds & Rates
    '10-Year Treasury Yield': '^TNX',
    '2-Year Treasury Yield': '^IRX',
    '30-Year Treasury Yield': '^TYX',
    
    # Currencies
    'DXY (US Dollar Index)': 'DXY=F',
    'EUR/USD': 'EURUSD=X',
    'GBP/USD': 'GBPUSD=X',
    'USD/JPY': 'USDJPY=X',
    'USD/CNY': 'CNY=X',
    'USD/INR': 'INR=X',
    
    # Commodities
    'Gold (XAU/USD)': 'GC=F',
    'Silver (XAG/USD)': 'SI=F',
    'Crude Oil (WTI)': 'CL=F',
    'Crude Oil (Brent)': 'BZ=F',
    'Copper': 'HG=F',
    'Natural Gas': 'NG=F',
    'Palladium': 'PA=F',
    'Platinum': 'PL=F',
    
    # Crypto
    'Bitcoin': 'BTC-USD',
    'Ethereum (ETH)': 'ETH-USD',
    'Binance Coin (BNB)': 'BNB-USD',
    'Ripple (XRP)': 'XRP-USD',
    'Litecoin (LTC)': 'LTC-USD',
    'Cardano (ADA)': 'ADA-USD',
    'Solana (SOL)': 'SOL-USD',
    'Polkadot (DOT)': 'DOT-USD',
    
    # Volatility & Risk
    'VIX (CBOE Volatility Index)': '^VIX',
    'Put/Call Ratio': '^SKEW',  # Note: SKEW is volatility skew, not put/call
    
    # Other
    'Nasdaq100': '^NDX',
    'DXY Index': 'DXY=F',
    'High Yield Spread': '^HYG',
    'Investment Grade Spread': '^LQD',
}

# ============================================================================
# DATA SOURCE PREFERENCES
# ============================================================================

# Primary data source
PRIMARY_DATA_SOURCE = 'yfinance'  # 'yfinance' or 'custom'

# Fallback sources (if primary fails)
FALLBACK_SOURCES = ['yfinance']

# Data frequency ('daily', 'weekly', 'monthly')
DATA_FREQUENCY = 'daily'

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

LOG_FILE = 'btc_analysis.log'
LOG_LEVEL = 'INFO'  # 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'

# Log to console as well as file
LOG_TO_CONSOLE = True

# ============================================================================
# REPORT CONFIGURATION
# ============================================================================

# Generate summary reports
GENERATE_SUMMARY_CSV = True
GENERATE_SUMMARY_PDF = True

# Include chart images in PDF (increases file size)
EMBED_CHARTS_IN_PDF = True

# Interpretation style ('technical', 'descriptive', 'minimal')
INTERPRETATION_STYLE = 'descriptive'

# ============================================================================
# PERFORMANCE & CACHING
# ============================================================================

# Cache fetched data to minimize API calls
USE_DATA_CACHE = True
CACHE_EXPIRY_HOURS = 24

# Number of retry attempts for failed API calls
API_RETRY_ATTEMPTS = 1

# Timeout for API calls (seconds)
API_TIMEOUT_SECONDS = 30

# ============================================================================
# ANALYSIS SETTINGS
# ============================================================================

# Calculate additional metrics
CALCULATE_BETA = True              # Beta coefficient
CALCULATE_SHARPE = False           # Sharpe ratio (requires risk-free rate)
CALCULATE_ROLLING_STATS = True     # Rolling correlation, beta, etc.

# Correlation methods to use
CORRELATION_METHODS = ['pearson', 'spearman']  # Add 'kendall' for Kendall tau

# Statistical tests
PERFORM_COINTEGRATION_TEST = False  # Johansen cointegration test
PERFORM_GRANGER_CAUSALITY = False   # Granger causality test (requires statsmodels)

# ============================================================================
# ADVANCED SETTINGS
# ============================================================================

# Normalization method for visualization ('minmax', 'zscore', 'returns')
NORMALIZATION_METHOD = 'minmax'

# Handle missing data ('forward_fill', 'interpolate', 'drop')
MISSING_DATA_STRATEGY = 'forward_fill'

# Maximum forward fill periods
MAX_FORWARD_FILL_PERIODS = 5

# ============================================================================
# EMAIL/NOTIFICATION SETTINGS (for future use)
# ============================================================================

# Send reports via email
SEND_EMAIL_REPORTS = False
EMAIL_RECIPIENTS = []  # ['user@example.com']
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587

# ============================================================================
# FILTERS & EXCLUSIONS
# ============================================================================

# Factors to exclude from analysis
EXCLUDED_FACTORS = []

# Only include factors matching pattern (None = no filter)
INCLUDED_FACTORS_PATTERN = None  # e.g., r'^(S&P|NASDAQ)'

# ============================================================================
# HELPERS
# ============================================================================

def get_date_range():
    """Get configured date range"""
    end_date = END_DATE or datetime.now().strftime('%Y-%m-%d')
    start_date = START_DATE or (datetime.now() - timedelta(days=DEFAULT_LOOKBACK_DAYS)).strftime('%Y-%m-%d')
    return start_date, end_date


def get_output_dir():
    """Get output directory as Path object"""
    return Path(OUTPUT_DIR)


def get_custom_factors():
    """Get custom factor mappings"""
    return CUSTOM_FACTORS.copy()


def load_config_from_json(json_path: str):
    """Load configuration from JSON file"""
    try:
        with open(json_path, 'r') as f:
            config_dict = json.load(f)
        return config_dict
    except Exception as e:
        print(f"Error loading config from {json_path}: {e}")
        return {}


def save_config_to_json(json_path: str):
    """Save current configuration to JSON file"""
    config_dict = {
        'START_DATE': START_DATE,
        'END_DATE': END_DATE,
        'MAX_FACTORS_PER_RUN': MAX_FACTORS_PER_RUN,
        'OUTPUT_DIR': OUTPUT_DIR,
        'CUSTOM_FACTORS': CUSTOM_FACTORS,
        'LOG_LEVEL': LOG_LEVEL,
    }
    
    try:
        with open(json_path, 'w') as f:
            json.dump(config_dict, f, indent=2)
        print(f"Configuration saved to {json_path}")
    except Exception as e:
        print(f"Error saving config to {json_path}: {e}")


if __name__ == '__main__':
    """Print current configuration"""
    print("Bitcoin Factor Analysis - Configuration")
    print("=" * 60)
    print(f"Start Date:        {START_DATE}")
    print(f"End Date:          {END_DATE}")
    print(f"Max Factors:       {MAX_FACTORS_PER_RUN}")
    print(f"Output Directory:  {OUTPUT_DIR}")
    print(f"Chart DPI:         {CHART_DPI}")
    print(f"Log Level:         {LOG_LEVEL}")
    print(f"Custom Factors:    {len(CUSTOM_FACTORS)}")
    print("=" * 60)
    
    print(f"\nDate Range: {get_date_range()}")
    print(f"Output Dir: {get_output_dir()}")
