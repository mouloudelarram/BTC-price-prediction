"""Data loading and preprocessing."""

import time
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict
import requests
import pandas as pd

from app.utils.logger import get_logger
from config import BINANCE_BASE_URL, BINANCE_SYMBOL, BINANCE_INTERVAL

logger = get_logger(__name__)


class BinanceDataLoader:
    """Load BTC price data from Binance public API."""

    def __init__(self, base_url: str = BINANCE_BASE_URL, symbol: str = BINANCE_SYMBOL):
        self.base_url = base_url
        self.symbol = symbol
        self.interval = BINANCE_INTERVAL

    def fetch_klines(self, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Fetch daily OHLCV klines from Binance.

        Args:
            start_date: 'YYYY-MM-DD'
            end_date: 'YYYY-MM-DD'

        Returns:
            DataFrame with OHLCV data
        """
        start_ms = self._date_to_ms(start_date)
        end_dt = datetime.fromisoformat(end_date).replace(tzinfo=timezone.utc) + timedelta(days=2)
        end_ms = int(end_dt.timestamp() * 1000)

        url = f"{self.base_url}/api/v3/klines"
        params = {
            "symbol": self.symbol,
            "interval": self.interval,
            "startTime": start_ms,
            "endTime": end_ms,
            "limit": 100,
        }

        try:
            resp = requests.get(url, params=params, timeout=10)
            resp.raise_for_status()
            raw = resp.json()

            if not raw:
                return pd.DataFrame()

            cols = ["open_time", "open", "high", "low", "close", "volume",
                    "close_time", "quote_asset_volume", "num_trades",
                    "taker_buy_base", "taker_buy_quote", "ignore"]
            df = pd.DataFrame(raw, columns=cols)
            df["open_time"] = pd.to_numeric(df["open_time"])
            df["close"] = pd.to_numeric(df["close"])
            df["open"] = pd.to_numeric(df["open"])
            df["date"] = pd.to_datetime(df["open_time"], unit="ms", utc=True).dt.date

            logger.info(f"Fetched {len(df)} klines from {start_date} to {end_date}")
            return df[["open_time", "date", "open", "high", "low", "close", "volume"]]

        except Exception as e:
            logger.error(f"Error fetching klines: {e}")
            raise

    def get_current_price(self) -> float:
        """Fetch latest BTC/USDT price."""
        url = f"{self.base_url}/api/v3/ticker/price"
        try:
            resp = requests.get(url, params={"symbol": self.symbol}, timeout=10)
            resp.raise_for_status()
            price = float(resp.json()["price"])
            logger.debug(f"Current {self.symbol} price: {price}")
            return price
        except Exception as e:
            logger.error(f"Error fetching current price: {e}")
            raise

    def fetch_next_close(self, date_str: str) -> Dict:
        """
        Fetch BTC close price on date and next available close.

        Returns:
            Dict with: date, close, next_date, next_close, live (bool)
        """
        dt = datetime.fromisoformat(date_str).date()
        start = (dt - timedelta(days=0)).isoformat()
        end = (dt + timedelta(days=7)).isoformat()

        try:
            df = self.fetch_klines(start, end)
            if df.empty:
                raise RuntimeError(f"No price data for {self.symbol} around {date_str}")

            # Find close on or before requested date
            prior = df[df["date"].apply(lambda x: x <= dt)]
            if prior.empty:
                raise RuntimeError(f"No close on or before {date_str}")

            close_date = prior["date"].iat[-1]
            close_price = float(prior["close"].iat[-1])

            # Find next close after that date
            later = df[df["date"].apply(lambda x: x > close_date)]

            if later.empty:
                today = datetime.now(timezone.utc).date()
                if close_date >= today - timedelta(days=1):
                    live_price = self.get_current_price()
                    return {
                        "date": close_date.isoformat(),
                        "close": close_price,
                        "next_date": today.isoformat(),
                        "next_close": live_price,
                        "live": True,
                    }
                return {
                    "date": close_date.isoformat(),
                    "close": close_price,
                    "next_date": None,
                    "next_close": None,
                    "live": False,
                }

            next_date = later["date"].iat[0]
            next_close = float(later["close"].iat[0])

            return {
                "date": close_date.isoformat(),
                "close": close_price,
                "next_date": next_date.isoformat(),
                "next_close": next_close,
                "live": False,
            }

        except Exception as e:
            logger.error(f"Error fetching next close: {e}")
            raise

    @staticmethod
    def _date_to_ms(date_str: str) -> int:
        """Convert 'YYYY-MM-DD' to UTC milliseconds."""
        dt = datetime.fromisoformat(date_str).replace(tzinfo=timezone.utc)
        return int(dt.timestamp() * 1000)
