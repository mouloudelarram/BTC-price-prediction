#!/usr/bin/env python
"""
Quick Start Example - Bitcoin Factor Analysis

This script provides simple examples of using the BTCFactorAnalyzer
for different analysis scenarios.
"""

from btc_factor_analyzer import (
    BTCFactorAnalyzer,
    DataFetcher,
    DataProcessor,
    ReportGenerator,
    FactorExtractor
)
from pathlib import Path
import pandas as pd


def example_1_basic_analysis():
    """
    Example 1: Run basic analysis on factors from factors.txt
    """
    print("\n" + "="*60)
    print("EXAMPLE 1: Basic Analysis from factors.txt")
    print("="*60)
    
    factors_file = Path('factors.txt')
    
    # Create analyzer
    analyzer = BTCFactorAnalyzer(
        factors_file=str(factors_file),
        output_dir='BTC_Factor_Reports',
        start_date='2022-01-01',
        end_date=None
    )
    
    # Run analysis on first 10 factors
    results = analyzer.run_analysis(max_factors=10)
    
    # Print summary
    print(f"\n✓ Analyzed {len(results['factors_analyzed'])} factors")
    print(f"✗ Failed: {len(results['factors_failed'])} factors\n")
    
    for item in results['factors_analyzed']:
        corr = item['correlation']
        symbol = "📈" if corr > 0.5 else "📉" if corr < -0.5 else "➡️"
        print(f"{symbol} {item['factor']:30s} | Correlation: {corr:7.4f}")
    
    print(f"\nOutput: {results['output_dir']}")


def example_2_custom_factors():
    """
    Example 2: Analyze specific custom factors
    """
    print("\n" + "="*60)
    print("EXAMPLE 2: Custom Factor Analysis")
    print("="*60)
    
    # Create a custom factors list
    custom_factors = [
        'S&P 500',
        'NASDAQ 100',
        'Gold (XAU/USD)',
        'Ethereum (ETH)',
        'DXY (US Dollar Index)',
        '10-Year Treasury Yield',
        'Crude Oil (WTI)',
        'VIX (CBOE Volatility Index)',
    ]
    
    # Fetch BTC data
    fetcher = DataFetcher(start_date='2021-01-01', end_date=None)
    btc_data = fetcher.fetch_btc_data()
    
    if btc_data is None:
        print("Failed to fetch BTC data")
        return
    
    print(f"\n📊 BTC Data: {len(btc_data)} records")
    print(f"   Period: {btc_data['Date'].min().date()} to {btc_data['Date'].max().date()}\n")
    
    # Create report generator
    report_gen = ReportGenerator('BTC_Custom_Analysis')
    processor = DataProcessor()
    
    # Analyze each factor
    print("Analyzing factors...")
    for factor in custom_factors:
        print(f"\n  → {factor}")
        
        # Fetch factor data
        factor_data = fetcher.fetch_factor_data(factor)
        if factor_data is None:
            print(f"    ⚠ No data")
            continue
        
        # Align data
        aligned, _ = processor.align_data(btc_data, factor_data)
        if aligned is None:
            print(f"    ⚠ Alignment failed")
            continue
        
        # Calculate stats
        stats = processor.calculate_statistics(
            aligned['Close_BTC'],
            aligned['Close_Factor']
        )
        
        corr = stats.get('correlation', 0)
        print(f"    ✓ Correlation: {corr:.4f} (n={len(aligned)})")


def example_3_analyze_crypto_assets():
    """
    Example 3: Analyze correlation between BTC and other cryptocurrencies
    """
    print("\n" + "="*60)
    print("EXAMPLE 3: Cryptocurrency Correlations")
    print("="*60)
    
    crypto_assets = [
        'Bitcoin',
        'Ethereum (ETH)',
        'Binance Coin (BNB)',
        'Ripple (XRP)',
    ]
    
    fetcher = DataFetcher(start_date='2021-01-01', end_date=None)
    processor = DataProcessor()
    
    # Fetch BTC
    btc_data = fetcher.fetch_btc_data()
    if btc_data is None:
        print("Failed to fetch BTC data")
        return
    
    print(f"\n📊 Analyzing {len(crypto_assets)-1} cryptocurrencies vs BTC\n")
    
    correlations = []
    for asset in crypto_assets:
        if asset == 'Bitcoin':
            continue
        
        print(f"  → {asset}")
        
        # Fetch asset data
        asset_data = fetcher.fetch_factor_data(asset)
        if asset_data is None:
            print(f"    ⚠ No data")
            continue
        
        # Align
        aligned, _ = processor.align_data(btc_data, asset_data)
        if aligned is None:
            print(f"    ⚠ Alignment failed")
            continue
        
        # Stats
        stats = processor.calculate_statistics(
            aligned['Close_BTC'],
            aligned['Close_Factor']
        )
        
        corr = stats.get('correlation', 0)
        correlations.append({'Asset': asset, 'Correlation': corr})
        print(f"    ✓ Correlation: {corr:.4f}")
    
    # Sort by correlation
    corr_df = pd.DataFrame(correlations).sort_values('Correlation', ascending=False)
    print("\n📈 Ranked by Correlation to BTC:")
    print(corr_df.to_string(index=False))


def example_4_date_range_analysis():
    """
    Example 4: Compare correlations across different time periods
    """
    print("\n" + "="*60)
    print("EXAMPLE 4: Time Period Analysis")
    print("="*60)
    
    factors = ['S&P 500', 'Gold (XAU/USD)', 'VIX (CBOE Volatility Index)']
    time_periods = [
        ('2023-01-01', '2023-06-30', 'H1 2023'),
        ('2023-07-01', '2023-12-31', 'H2 2023'),
        ('2024-01-01', '2024-02-15', '2024 YTD'),
    ]
    
    processor = DataProcessor()
    
    print(f"\nComparing {len(factors)} factors across {len(time_periods)} periods\n")
    
    for start, end, label in time_periods:
        print(f"\n{label}:")
        print("-" * 50)
        
        fetcher = DataFetcher(start_date=start, end_date=end)
        btc_data = fetcher.fetch_btc_data()
        
        if btc_data is None or len(btc_data) < 10:
            print(f"  ⚠ Insufficient data")
            continue
        
        for factor in factors:
            factor_data = fetcher.fetch_factor_data(factor)
            if factor_data is None:
                continue
            
            aligned, _ = processor.align_data(btc_data, factor_data)
            if aligned is None or len(aligned) < 5:
                continue
            
            stats = processor.calculate_statistics(
                aligned['Close_BTC'],
                aligned['Close_Factor']
            )
            
            corr = stats.get('correlation', 0)
            print(f"  {factor:30s}: {corr:7.4f}")


def example_5_factor_extraction():
    """
    Example 5: Extract and list available factors from factors.txt
    """
    print("\n" + "="*60)
    print("EXAMPLE 5: Available Factors")
    print("="*60)
    
    extractor = FactorExtractor('factors.txt')
    factors = extractor.extract_factors()
    
    print(f"\nFound {len(factors)} factors in factors.txt:\n")
    
    for i, factor in enumerate(factors[:20], 1):
        # Check if we have a ticker mapping
        has_mapping = factor in DataFetcher.TICKER_MAPPING
        status = "✓" if has_mapping else "✗"
        print(f"  {status} {i:2d}. {factor}")
    
    if len(factors) > 20:
        print(f"\n  ... and {len(factors) - 20} more")
    
    print(f"\nNote: ✓ = has Yahoo Finance ticker, ✗ = needs custom mapping")


if __name__ == '__main__':
    print("\n" + "="*60)
    print("Bitcoin Factor Analysis - Quick Start Examples")
    print("="*60)
    
    examples = [
        ('1', 'Basic Analysis (factors.txt)', example_1_basic_analysis),
        ('2', 'Custom Factors', example_2_custom_factors),
        ('3', 'Cryptocurrency Correlations', example_3_analyze_crypto_assets),
        ('4', 'Time Period Analysis', example_4_date_range_analysis),
        ('5', 'List Available Factors', example_5_factor_extraction),
    ]
    
    print("\nAvailable Examples:")
    for key, desc, _ in examples:
        print(f"  {key}. {desc}")
    
    print("\nRun examples:")
    print("  python examples.py           # Run all examples")
    print("  python -c \"from examples import example_1_basic_analysis; example_1_basic_analysis()\"")
    
    print("\nRunning Example 5 (List Factors)...")
    example_5_factor_extraction()
    
    print("\n" + "="*60)
    print("For more examples, uncomment the example functions at the bottom")
    print("="*60 + "\n")
    
    # Uncomment to run other examples:
    # example_1_basic_analysis()
    # example_2_custom_factors()
    # example_3_analyze_crypto_assets()
    # example_4_date_range_analysis()
