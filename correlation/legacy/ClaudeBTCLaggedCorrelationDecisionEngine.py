"""
BTC Trading Signal Generator
Based on Lagged Cross-Asset Correlation Analysis

This module parses correlation analysis output and generates BUY/SELL signals
for Bitcoin based on correlation patterns across multiple timeframes and lag periods.
"""

import re
import sys
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class SignalResult:
    """Container for signal generation results"""
    signal: str  # "BUY" or "SELL"
    score: float
    confidence: float
    short_term_avg: float
    mid_term_avg: float
    long_term_avg: float
    reason: str
    details: Dict


class BTCSignalGenerator:
    """
    Analyzes lagged correlation data to generate BTC trading signals
    """
    
    # Asset categories for contextual analysis
    RISK_ON_ASSETS = {
        'ARKW', 'IGV', 'XLK', 'QQQ', 'SOXX', 'VGT', 'FDN', 'ARKK',
        'ETH-USD', 'SOL-USD', 'RAY-USD', 'MATIC-USD', 'AVAX-USD'
    }
    
    RISK_OFF_ASSETS = {
        'GLD', 'TLT', 'IEF', 'SHY', 'AGG', 'BND', 'VCSH', 'GOVT'
    }
    
    # Timeframe definitions
    SHORT_TERM = ['1mo', '3mo']
    MID_TERM = ['6mo', '1y']
    LONG_TERM = ['2y', '3y']
    
    def __init__(self, buy_threshold: float = 0.0, verbose: bool = True):
        """
        Initialize signal generator
        
        Args:
            buy_threshold: Score threshold for BUY signal (default: 0.0)
            verbose: Print detailed analysis (default: True)
        """
        self.buy_threshold = buy_threshold
        self.verbose = verbose
        self.data = None
        
    def parse_correlation_file(self, filepath: str) -> pd.DataFrame:
        """
        Parse correlation analysis text file into structured DataFrame
        by delegating to parse_correlation_text for robust parsing.
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        return self.parse_correlation_text(content)
    
    def parse_correlation_text(self, text: str) -> pd.DataFrame:
        """
        Parse correlation analysis text string into structured DataFrame.

        This parser is tolerant to two common formats produced by
        `btc_lagged_correlation_analysis()`:
         - compact single-line blocks (asset corr asset corr ...)
         - DataFrame-style printed blocks where the top-3 rows are shown

        It finds each section header and then scans following lines
        to extract the first three ticker+correlation pairs.
        """
        header_re = re.compile(r'--- Analysis for Period:\s*(?P<period>\S+)\s*with Shift of\s*(?P<shift>\d+) day\(s\)\s*---')
        asset_re = re.compile(r'^(?P<ticker>[\^A-Za-z0-9\-]+)\s+(-?\d+\.\d+)')

        lines = text.splitlines()
        records = []
        i = 0
        while i < len(lines):
            line = lines[i]
            m = header_re.search(line)
            if m:
                period = m.group('period')
                shift = int(m.group('shift'))
                # scan next lines to find up to 3 asset-corr rows
                found = 0
                j = i + 1
                assets = []
                while j < len(lines) and found < 3:
                    l = lines[j].strip()
                    # Try matching DataFrame-style row: index + ticker + corr + period + shift
                    # e.g. "0    EWA     0.539587    1mo           1"
                    df_row_match = re.match(r'^\d+\s+([\^A-Za-z0-9\-]+)\s+(-?\d+\.\d+)', l)
                    if df_row_match:
                        ticker = df_row_match.group(1)
                        corr = float(df_row_match.group(2))
                        assets.append((ticker, corr))
                        found += 1
                        j += 1
                        continue

                    # Try matching compact format: TICKER 0.xxx
                    compact_match = re.match(r'^([\^A-Za-z0-9\-]+)\s+(-?\d+\.\d+)', l)
                    if compact_match:
                        ticker = compact_match.group(1)
                        corr = float(compact_match.group(2))
                        assets.append((ticker, corr))
                        found += 1
                        j += 1
                        continue

                    # If line empty or unrelated, advance
                    j += 1

                if len(assets) >= 1:
                    # pad with NaNs if fewer than 3 found
                    while len(assets) < 3:
                        assets.append((None, float('nan')))
                    records.append({
                        'period': period,
                        'shift_days': shift,
                        'asset1': assets[0][0],
                        'corr1': assets[0][1],
                        'asset2': assets[1][0],
                        'corr2': assets[1][1],
                        'asset3': assets[2][0],
                        'corr3': assets[2][1],
                    })
                i = j
            else:
                i += 1

        if not records:
            raise ValueError("No correlation data found in text. Check format.")

        self.data = pd.DataFrame(records)
        return self.data
    
    def compute_metrics(self) -> Dict:
        """
        Compute key metrics from correlation data
        
        Returns:
            Dictionary of computed metrics
        """
        if self.data is None:
            raise ValueError("No data loaded. Call parse_correlation_file() first.")
        
        # Calculate average correlation per row
        self.data['avg_corr'] = self.data[['corr1', 'corr2', 'corr3']].mean(axis=1)
        self.data['max_corr'] = self.data[['corr1', 'corr2', 'corr3']].max(axis=1)
        self.data['min_corr'] = self.data[['corr1', 'corr2', 'corr3']].min(axis=1)
        
        metrics = {}
        
        # Timeframe-based metrics
        metrics['short_term_avg'] = self.data[
            self.data['period'].isin(self.SHORT_TERM)
        ]['avg_corr'].mean()
        
        metrics['mid_term_avg'] = self.data[
            self.data['period'].isin(self.MID_TERM)
        ]['avg_corr'].mean()
        
        metrics['long_term_avg'] = self.data[
            self.data['period'].isin(self.LONG_TERM)
        ]['avg_corr'].mean()
        
        # Maximum correlations by timeframe
        metrics['short_term_max'] = self.data[
            self.data['period'].isin(self.SHORT_TERM)
        ]['max_corr'].max()
        
        metrics['mid_term_max'] = self.data[
            self.data['period'].isin(self.MID_TERM)
        ]['max_corr'].max()
        
        # Correlation decay analysis
        metrics['correlation_decay'] = (
            metrics['short_term_avg'] - metrics['long_term_avg']
        )
        
        # Shift day analysis
        short_shift_corr = self.data[
            (self.data['shift_days'] <= 2) & 
            (self.data['period'].isin(self.SHORT_TERM + self.MID_TERM))
        ]['avg_corr'].mean()
        
        long_shift_corr = self.data[
            (self.data['shift_days'] >= 4) & 
            (self.data['period'].isin(self.SHORT_TERM + self.MID_TERM))
        ]['avg_corr'].mean()
        
        metrics['shift_correlation_trend'] = long_shift_corr - short_shift_corr
        
        # Risk-on asset exposure
        risk_on_count = 0
        total_assets = 0
        for _, row in self.data.iterrows():
            for asset in [row['asset1'], row['asset2'], row['asset3']]:
                total_assets += 1
                if asset in self.RISK_ON_ASSETS:
                    risk_on_count += 1
        
        metrics['risk_on_ratio'] = risk_on_count / total_assets if total_assets > 0 else 0
        
        # Overall statistics
        metrics['overall_avg_corr'] = self.data['avg_corr'].mean()
        metrics['overall_max_corr'] = self.data['max_corr'].max()
        metrics['high_corr_count'] = len(self.data[self.data['max_corr'] > 0.7])
        metrics['very_high_corr_count'] = len(self.data[self.data['max_corr'] > 0.85])
        
        return metrics
    
    def generate_signal(self, metrics: Optional[Dict] = None) -> SignalResult:
        """
        Generate BUY/SELL signal based on correlation metrics
        
        Args:
            metrics: Pre-computed metrics (optional, will compute if not provided)
            
        Returns:
            SignalResult object with signal, score, confidence, and explanation
        """
        if metrics is None:
            metrics = self.compute_metrics()
        
        score = 0.0
        reasons = []
        
        # === BULLISH FACTORS ===
        
        # Strong short-term correlations (+3 points max)
        if metrics['short_term_avg'] > 0.7:
            points = min(3.0, (metrics['short_term_avg'] - 0.7) * 10)
            score += points
            reasons.append(f"Strong short-term correlations ({metrics['short_term_avg']:.3f}): +{points:.1f}")
        
        # Strong mid-term correlations (+2 points max)
        if metrics['mid_term_avg'] > 0.6:
            points = min(2.0, (metrics['mid_term_avg'] - 0.6) * 5)
            score += points
            reasons.append(f"Strong mid-term correlations ({metrics['mid_term_avg']:.3f}): +{points:.1f}")
        
        # Very high individual correlations (+2 points)
        if metrics['very_high_corr_count'] > 0:
            points = min(2.0, metrics['very_high_corr_count'] * 0.5)
            score += points
            reasons.append(f"Very high correlations (>0.85) found: {metrics['very_high_corr_count']} instances: +{points:.1f}")
        
        # Positive correlation with increasing lag (+1.5 points)
        if metrics['shift_correlation_trend'] > 0.05:
            points = min(1.5, metrics['shift_correlation_trend'] * 10)
            score += points
            reasons.append(f"Increasing correlation with lag: +{points:.1f}")
        
        # High risk-on asset presence (+1 point)
        if metrics['risk_on_ratio'] > 0.6:
            points = min(1.0, (metrics['risk_on_ratio'] - 0.6) * 2.5)
            score += points
            reasons.append(f"High risk-on asset exposure ({metrics['risk_on_ratio']:.2%}): +{points:.1f}")
        
        # Strong recent momentum (short > mid > long) (+1 point)
        if (metrics['short_term_avg'] > metrics['mid_term_avg'] > metrics['long_term_avg']):
            score += 1.0
            reasons.append("Positive momentum structure: +1.0")
        
        # === BEARISH FACTORS ===
        
        # Weak short-term correlations (-3 points max)
        if metrics['short_term_avg'] < 0.4:
            points = -min(3.0, (0.4 - metrics['short_term_avg']) * 7.5)
            score += points
            reasons.append(f"Weak short-term correlations ({metrics['short_term_avg']:.3f}): {points:.1f}")
        
        # Negative correlation decay (-2 points)
        if metrics['correlation_decay'] < -0.1:
            points = -min(2.0, abs(metrics['correlation_decay']) * 5)
            score += points
            reasons.append(f"Long-term stronger than short-term: {points:.1f}")
        
        # Overall weak correlations (-2 points)
        if metrics['overall_avg_corr'] < 0.3:
            points = -2.0
            score += points
            reasons.append(f"Overall weak correlation structure: {points:.1f}")
        
        # No high correlations found (-1.5 points)
        if metrics['high_corr_count'] == 0:
            score -= 1.5
            reasons.append("No significant correlations (>0.7) found: -1.5")
        
        # Determine signal
        if score > self.buy_threshold:
            signal = "BUY"
        else:
            signal = "SELL"
        
        # Calculate confidence (0-100%)
        # Based on signal strength and consistency
        confidence = min(100, 50 + abs(score) * 10)
        
        # Generate summary reason
        if signal == "BUY":
            summary = "Strong short/mid-term predictive correlations with risk-on assets"
        else:
            summary = "Weak correlation structure suggests limited predictive power"
        
        return SignalResult(
            signal=signal,
            score=score,
            confidence=confidence,
            short_term_avg=metrics['short_term_avg'],
            mid_term_avg=metrics['mid_term_avg'],
            long_term_avg=metrics['long_term_avg'],
            reason=summary,
            details={
                'metrics': metrics,
                'reasons': reasons
            }
        )
    
    def analyze(self, source: str, is_filepath: bool = True) -> SignalResult:
        """
        Complete analysis pipeline: parse, compute metrics, generate signal
        
        Args:
            source: File path or text string containing correlation data
            is_filepath: If True, treat source as file path; if False, as text string
            
        Returns:
            SignalResult object
        """
        # Parse data
        if is_filepath:
            self.parse_correlation_file(source)
        else:
            self.parse_correlation_text(source)
        
        # Compute metrics
        metrics = self.compute_metrics()
        
        # Generate signal
        result = self.generate_signal(metrics)
        
        # Print results if verbose
        if self.verbose:
            self.print_results(result)
        
        return result
    
    def print_results(self, result: SignalResult):
        """
        Print formatted analysis results
        
        Args:
            result: SignalResult object to display
        """
        print("\n" + "="*70)
        print("BTC TRADING SIGNAL ANALYSIS")
        print("="*70)
        
        print(f"\n📊 CORRELATION METRICS:")
        print(f"  Short-term avg (1mo-3mo):  {result.short_term_avg:.3f}")
        print(f"  Mid-term avg (6mo-1y):     {result.mid_term_avg:.3f}")
        print(f"  Long-term avg (2y-3y):     {result.long_term_avg:.3f}")
        
        print(f"\n🎯 SIGNAL GENERATION:")
        print(f"  Signal Score:  {result.score:+.2f}")
        print(f"  Decision:      {result.signal} BTC")
        print(f"  Confidence:    {result.confidence:.0f}%")
        
        print(f"\n💡 REASONING:")
        print(f"  {result.reason}")
        
        print(f"\n📝 DETAILED SCORING:")
        for reason in result.details['reasons']:
            print(f"  • {reason}")
        
        print("\n" + "="*70 + "\n")


def main():
    """
    Example usage of BTCSignalGenerator
    """
    # Example correlation data (you would load from actual file)
    example_data = ""
    with open(sys.argv[1], "r") as f:
        example_data = f.read()

    
    # Initialize generator
    generator = BTCSignalGenerator(buy_threshold=0.0, verbose=True)
    
    # Analyze (use is_filepath=False for text string)
    result = generator.analyze(example_data, is_filepath=False)
    
    # Access results programmatically
    print(f"Programmatic access: Signal={result.signal}, Score={result.score:.2f}")
    
    # return BUY or SELL signal and detailed info for potential further use
    return result.signal, result


if __name__ == "__main__":
    main()