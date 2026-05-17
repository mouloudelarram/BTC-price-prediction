"""Signal generation engine for BTC trading decisions."""

import re
import pandas as pd
import yfinance as yf
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

from app.utils.logger import get_logger
from app.models import SignalResponse, Contributor
from config import (
    SIGNAL_WEIGHTS, SIGNAL_CORRELATION_THRESHOLDS,
    SIGNAL_BUY_THRESHOLD, SIGNAL_SELL_THRESHOLD
)

logger = get_logger(__name__)


class SignalEngine:
    """Generate BUY/SELL/HOLD trading signals based on correlation data."""

    def __init__(self):
        self.weights = SIGNAL_WEIGHTS
        self.thresholds = SIGNAL_CORRELATION_THRESHOLDS
        self.buy_threshold = SIGNAL_BUY_THRESHOLD
        self.sell_threshold = SIGNAL_SELL_THRESHOLD

    def generate_signal(self, correlation_summary_path: Path) -> SignalResponse:
        """
        Generate trading signal based on correlation summary file.

        Args:
            correlation_summary_path: Path to correlation analysis output

        Returns:
            SignalResponse with BUY/SELL/HOLD recommendation
        """
        logger.info(f"Generating signal from {correlation_summary_path}")

        # Parse correlation file
        df = self._parse_correlation_file(correlation_summary_path)
        if df.empty:
            logger.error("No data found in correlation file")
            return self._create_hold_signal()

        # Filter by thresholds
        df = self._filter_by_thresholds(df)
        logger.info(f"Processing {len(df)} significant assets after filtering")

        # Calculate signal
        total_score, max_potential, contributors = self._calculate_score(df)

        # Determine final signal
        signal, confidence = self._determine_signal(total_score, max_potential)

        result = SignalResponse(
            timestamp=datetime.utcnow().isoformat() + "Z",
            signal=signal,
            confidence=f"{confidence:.1f}%",
            net_score=round(total_score, 2),
            analyzed_count=len(contributors),
            top_contributors=sorted(
                contributors,
                key=lambda x: abs(x.impact),
                reverse=True
            )[:5]
        )

        logger.info(f"Signal generated: {signal} (score={total_score}, confidence={confidence}%)")
        return result

    def _parse_correlation_file(self, file_path: Path) -> pd.DataFrame:
        """Extract correlation data from text summary file."""
        data = []
        current_period = None
        current_shift = None

        try:
            with open(file_path, 'r') as f:
                for line in f:
                    # Match header lines like "Period: 1mo with Shift of 1"
                    header_match = re.search(r"Period: (\w+) with Shift of (\d+)", line)
                    if header_match:
                        current_period, current_shift = header_match.groups()
                        current_shift = int(current_shift)
                        continue

                    # Match data lines starting with number
                    if re.match(r"^\s*\d+\s+", line) and "Ticker" not in line:
                        parts = line.split()
                        if len(parts) >= 3:
                            try:
                                data.append({
                                    "ticker": parts[1],
                                    "correlation": float(parts[2]),
                                    "period": current_period,
                                    "shift_days": current_shift
                                })
                            except (ValueError, IndexError):
                                logger.warning(f"Could not parse line: {line}")
                                continue

            result_df = pd.DataFrame(data)
            logger.debug(f"Parsed {len(result_df)} correlation records")
            return result_df

        except Exception as e:
            logger.error(f"Error parsing correlation file: {e}")
            return pd.DataFrame()

    def _filter_by_thresholds(self, df: pd.DataFrame) -> pd.DataFrame:
        """Filter assets by correlation thresholds."""
        def meets_threshold(row):
            threshold = (
                self.thresholds["short_term"]
                if row['period'] in ['1mo', '3mo']
                else self.thresholds["long_term"]
            )
            return abs(row['correlation']) >= threshold

        filtered = df[df.apply(meets_threshold, axis=1)].copy()
        logger.debug(f"Filtered {len(df)} → {len(filtered)} assets by threshold")
        return filtered

    def _calculate_score(self, df: pd.DataFrame) -> tuple:
        """
        Calculate signal score from asset correlations and market direction.

        Returns:
            Tuple of (total_score, max_potential, contributors)
        """
        total_score = 0.0
        max_potential = 0.0
        contributors = []

        for _, row in df.iterrows():
            try:
                direction = self._get_market_direction(row['ticker'], row['shift_days'])
                weight = self.weights.get(row['period'], 1.0)
                impact_value = row['correlation'] * weight

                contribution = impact_value * direction
                total_score += contribution
                max_potential += impact_value

                if direction != 0:
                    contributors.append(
                        Contributor(
                            ticker=row['ticker'],
                            impact=round(contribution, 3),
                            period=row['period'],
                            move="UP" if direction > 0 else "DOWN"
                        )
                    )

            except Exception as e:
                logger.warning(f"Error processing {row['ticker']}: {e}")
                continue

        return total_score, max_potential, contributors

    def _determine_signal(self, total_score: float, max_potential: float) -> tuple:
        """
        Determine final signal based on score.

        Returns:
            Tuple of (signal, confidence_pct)
        """
        if total_score >= self.buy_threshold:
            signal = "BUY"
        elif total_score <= self.sell_threshold:
            signal = "SELL"
        else:
            signal = "HOLD"

        confidence = (
            (abs(total_score) / max_potential * 100)
            if max_potential > 0
            else 0.0
        )

        return signal, confidence

    def _get_market_direction(self, ticker: str, shift_days: int) -> int:
        """
        Fetch market data and determine direction (1=UP, -1=DOWN, 0=NEUTRAL).

        Args:
            ticker: Asset ticker symbol
            shift_days: Number of days to compare

        Returns:
            1 if price up, -1 if price down, 0 if neutral or error
        """
        try:
            t = yf.Ticker(ticker)
            hist = t.history(period="1mo", interval="1d")

            if hist.empty or len(hist) < shift_days + 1:
                logger.debug(f"Insufficient data for {ticker}")
                return 0

            price_now = hist['Close'].iloc[-1]
            price_then = hist['Close'].iloc[-(shift_days + 1)]

            if price_now > price_then:
                return 1
            elif price_now < price_then:
                return -1
            else:
                return 0

        except Exception as e:
            logger.warning(f"Error fetching direction for {ticker}: {e}")
            return 0

    def _create_hold_signal(self) -> SignalResponse:
        """Create a HOLD signal with no confidence."""
        return SignalResponse(
            timestamp=datetime.utcnow().isoformat() + "Z",
            signal="HOLD",
            confidence="0.0%",
            net_score=0.0,
            analyzed_count=0,
            top_contributors=[]
        )
