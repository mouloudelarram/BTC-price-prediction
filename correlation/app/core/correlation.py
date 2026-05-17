"""Correlation analysis engine for BTC prediction."""

import os
import time
import pandas as pd
import yfinance as yf
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pathlib import Path
from typing import List, Tuple

from app.utils.logger import get_logger
from app.utils.helpers import rotate_file
from config import (
    CORRELATION_PERIODS, CORRELATION_MAX_LAG_DAYS, CORRELATION_CHUNK_SIZE,
    CORRELATION_MAX_RETRIES, CORRELATION_BACKOFF_MULTIPLIER, ALL_TICKERS,
    RESULTS_DIR
)

logger = get_logger(__name__)


class CorrelationEngine:
    """Main correlation analysis engine."""

    def __init__(self):
        self.results_dir = RESULTS_DIR
        self.results_dir.mkdir(exist_ok=True)

    def analyze_lagged_correlation(
        self,
        period: str = "1y",
        shift_days: int = 1,
        plot: bool = False
    ) -> pd.DataFrame:
        """
        Perform lagged correlation analysis between BTC and other assets.

        Args:
            period: Analysis period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 3y, 5y, 10y)
            shift_days: Number of days to lag BTC returns
            plot: Whether to generate plots

        Returns:
            DataFrame with top 20 most correlated assets
        """
        if period not in ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "3y", "5y", "10y"]:
            raise ValueError(f"Invalid period: {period}")

        logger.info(f"Starting correlation analysis for period={period}, shift_days={shift_days}")

        # Download data with retry logic
        data = self._download_data(ALL_TICKERS, period)
        if data.empty or 'BTC-USD' not in data.columns:
            logger.error("BTC-USD not available in downloaded data")
            return pd.DataFrame()

        # Calculate returns and lag analysis
        returns = data.pct_change(fill_method=None).dropna()
        btc_lagged = returns['BTC-USD'].shift(shift_days).rename('BTC_Lagged')
        returns = pd.concat([returns, btc_lagged], axis=1).dropna()

        # Calculate correlations
        correlations = returns.corr()['BTC_Lagged'].drop(['BTC-USD', 'BTC_Lagged'])
        top_20 = correlations.sort_values(ascending=False).head(20)

        logger.info(f"Top correlations for period={period}, shift={shift_days}:\n{top_20}")

        # Optional visualization
        if plot:
            self._plot_correlations(top_20, period, shift_days)

        # Format as DataFrame
        result = top_20.reset_index()
        result.columns = ['Ticker', 'Correlation']
        result['period'] = period
        result['shift_days'] = shift_days

        return result

    def run_full_analysis(self) -> Tuple[Path, str]:
        """
        Run full correlation analysis across all periods and lags.

        Returns:
            Tuple of (summary_file_path, timestamp)
        """
        from datetime import datetime
        timestamp = datetime.utcnow().isoformat()

        summary_path = self.results_dir / "correlation_summary.txt"

        # Rotate old summary if exists
        if summary_path.exists():
            rotate_file(summary_path)

        logger.info(f"Writing correlation summary to {summary_path}")

        with open(summary_path, 'w') as f:
            f.write("=== Correlation Analysis Summary ===\n")
            f.write(f"Generated: {timestamp}\n\n")

            for period in CORRELATION_PERIODS:
                for shift in range(1, CORRELATION_MAX_LAG_DAYS + 1):
                    logger.info(f"Analyzing {period} with shift {shift}...")

                    f.write(f"\n--- Period: {period} with Shift of {shift} day(s) ---\n")

                    try:
                        result = self.analyze_lagged_correlation(period=period, shift_days=shift)
                        f.write(result.to_string(index=False))
                        f.write("\n")
                    except Exception as e:
                        logger.error(f"Error analyzing {period} shift {shift}: {e}")
                        f.write(f"Error: {e}\n")

        logger.info(f"Correlation summary saved to {summary_path}")
        return summary_path, timestamp

    def _download_data(
        self,
        tickers: List[str],
        period: str,
        chunk_size: int = CORRELATION_CHUNK_SIZE,
        max_retries: int = CORRELATION_MAX_RETRIES
    ) -> pd.DataFrame:
        """Download OHLCV data with retry logic."""
        parts = []
        backoff = CORRELATION_BACKOFF_MULTIPLIER

        for i in range(0, len(tickers), chunk_size):
            batch = tickers[i : i + chunk_size]
            attempt = 0

            while attempt < max_retries:
                try:
                    logger.debug(f"Downloading batch {i // chunk_size + 1}: {batch[:3]}...")
                    data = yf.download(batch, period=period, threads=False, progress=False)

                    if isinstance(data, pd.DataFrame):
                        if 'Close' in data.columns:
                            closes = data['Close']
                        else:
                            closes = data
                    else:
                        closes = data.to_frame() if isinstance(data, pd.Series) else data

                    parts.append(closes)
                    break

                except Exception as e:
                    attempt += 1
                    wait_time = backoff ** attempt
                    logger.warning(
                        f"Download error (attempt {attempt}/{max_retries}): {e}. "
                        f"Retrying in {wait_time:.1f}s..."
                    )
                    time.sleep(wait_time)
            else:
                logger.error(f"Failed to download after {max_retries} attempts: {batch}")

        if not parts:
            logger.error("No data downloaded")
            return pd.DataFrame()

        combined = pd.concat(parts, axis=1)

        # Flatten multiindex if needed
        if isinstance(combined.columns, pd.MultiIndex):
            if 'Close' in combined.columns.levels[0]:
                combined = combined['Close']

        if isinstance(combined, pd.Series):
            combined = combined.to_frame()

        # Remove all-NaN columns
        combined = combined.dropna(axis=1, how='all')

        logger.debug(f"Downloaded {combined.shape[1]} assets with {combined.shape[0]} rows")
        return combined

    def _plot_correlations(self, correlations: pd.Series, period: str, shift_days: int) -> None:
        """Generate and save correlation plot."""
        try:
            plt.figure(figsize=(12, 8))
            correlations.plot(kind='barh', color='skyblue')
            plt.title(f"Top Correlations with BTC (Lag={shift_days}d, Period={period})")
            plt.xlabel("Correlation Coefficient")
            plt.grid(axis='x', linestyle='--', alpha=0.7)
            plt.tight_layout()

            plot_path = self.results_dir / f"correlation_{period}_lag{shift_days}.png"
            plt.savefig(plot_path)
            plt.close('all')
            logger.info(f"Plot saved to {plot_path}")

        except Exception as e:
            logger.error(f"Error creating plot: {e}")
