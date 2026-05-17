"""Configuration management for Correlation Engine."""

import os
from pathlib import Path
from typing import Dict, List

# Project root
PROJECT_ROOT = Path(__file__).parent.absolute()

# API Configuration
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", 8000))
API_DEBUG = os.getenv("API_DEBUG", "False").lower() == "true"

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_DIR = PROJECT_ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)

# Data paths
RESULTS_DIR = PROJECT_ROOT / "results"
RESULTS_DIR.mkdir(exist_ok=True)

# Correlation Engine Configuration
CORRELATION_PERIODS = ["1mo", "3mo", "6mo", "1y", "2y", "3y"]
CORRELATION_MAX_LAG_DAYS = 7
CORRELATION_CHUNK_SIZE = 20
CORRELATION_MAX_RETRIES = 3
CORRELATION_BACKOFF_MULTIPLIER = 1.7

# Signal Engine Thresholds
SIGNAL_WEIGHTS: Dict[str, float] = {
    "1mo": 1.0,
    "3mo": 2.0,
    "6mo": 3.0,
    "1y": 5.0,
    "2y": 3.0,
    "3y": 2.0,
}

SIGNAL_CORRELATION_THRESHOLDS = {
    "short_term": 0.30,  # 1mo, 3mo
    "long_term": 0.20,   # 6mo and beyond
}

SIGNAL_BUY_THRESHOLD = 2.0
SIGNAL_SELL_THRESHOLD = -2.0

# Asset Lists for Correlation Analysis
OTHER_CRYPTOS = [
    'ETH-USD', 'ADA-USD', 'XRP-USD', 'SOL-USD', 'DOGE-USD', 'LTC-USD', 'BCH-USD',
    'LINK-USD', 'DOT-USD', 'UNI-USD', 'AVAX-USD', 'MATIC-USD', 'ATOM-USD', 'ALGO-USD',
    'VET-USD', 'FIL-USD', 'TRX-USD', 'XLM-USD', 'THETA-USD', 'AAVE-USD', 'EOS-USD',
    'MKR-USD', 'COMP-USD', 'SUSHI-USD', 'YFI-USD', 'CRV-USD', 'SNX-USD', 'ZRX-USD',
    'REN-USD', 'BAL-USD', 'GRT-USD', '1INCH-USD', 'KNC-USD', 'LRC-USD', 'OCEAN-USD',
    'UMA-USD', 'BAND-USD', 'SRM-USD', 'RUNE-USD', 'CRO-USD', 'FTT-USD', 'GNO-USD',
    'HNT-USD', 'KAVA-USD', 'LUNA-USD', 'NEAR-USD', 'RAY-USD', 'SAND-USD', 'STX-USD',
    'WAVES-USD', 'ZIL-USD'
]

STOCK_INDICES = [
    '^GSPC', '^DJI', '^IXIC', '^FTSE', '^N225', '^HSI', '^BSESN', '^MXX', '^AXJO',
    '^GDAXI', '^FCHI', '^AORD', '^SSMI', '^IBEX', '^TA125', '^KLSE', '^NZ50', '^OMX',
    '^RTS', '^SSEC'
]

ETFS = [
    'SPY', 'QQQ', 'DIA', 'IWM', 'VTI', 'VOO', 'IVV', 'VEA', 'VWO', 'EFA', 'EEM',
    'VUG', 'VTV', 'VBR', 'VOT', 'VXF'
]

SECTOR_ETFS = [
    'XLY', 'XLP', 'XLE', 'XLF', 'XLV', 'XLI', 'XLB', 'XLRE', 'XLK', 'XLU', 'XLC'
]

THEMATIC_ETFS = [
    'ARKK', 'ARKG', 'ARKW', 'ARKF', 'ARKQ', 'TAN', 'LIT', 'ICLN', 'PBW',
    'CLOU', 'SKYY', 'SOXX', 'IGV', 'CIBR', 'BOTZ'
]

INTERNATIONAL_ETFS = [
    'EEM', 'VWO', 'EWZ', 'EFA', 'VEA', 'IEMG', 'SCZ', 'GXC', 'FXI', 'MCHI',
    'EWJ', 'EWQ', 'EWG', 'EWC', 'EWA', 'EWY', 'EWT', 'INDA'
]

BONDS_COMMODITIES = [
    'TLT', 'GLD', 'SLV', 'USO', 'DBC', 'GSG', 'PDBC', 'BND', 'AGG', 'LQD',
    'JNK', 'HYG', 'SHY', 'IEI', 'IEF'
]

# All tickers for correlation analysis
ALL_TICKERS = (
    ["BTC-USD"] + OTHER_CRYPTOS + STOCK_INDICES + ETFS + SECTOR_ETFS +
    THEMATIC_ETFS + INTERNATIONAL_ETFS + BONDS_COMMODITIES
)

# Binance Configuration
BINANCE_BASE_URL = "https://api.binance.com"
BINANCE_SYMBOL = "BTCUSDT"
BINANCE_INTERVAL = "1d"

# Pipeline Configuration
PIPELINE_ENABLED = os.getenv("PIPELINE_ENABLED", "False").lower() == "true"
PIPELINE_SCHEDULE_HOUR = int(os.getenv("PIPELINE_SCHEDULE_HOUR", 0))  # Midnight UTC

# Cache Configuration
CACHE_TTL_SECONDS = int(os.getenv("CACHE_TTL_SECONDS", 3600))  # 1 hour
