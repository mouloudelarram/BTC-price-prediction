#!/usr/bin/env python
"""
Run Script for Bitcoin Factor Analysis

Simple entry point for running the analysis with different options
"""

import sys
import argparse
from pathlib import Path
from btc_factor_analyzer import BTCFactorAnalyzer
from config import (
    START_DATE, END_DATE, MAX_FACTORS_PER_RUN, OUTPUT_DIR,
    get_date_range, get_custom_factors
)


def print_banner():
    """Print welcome banner"""
    print("\n" + "="*70)
    print("  BITCOIN FACTOR ANALYSIS TOOL v1.0")
    print("="*70)
    print("  Automated analysis of BTC correlations with economic factors")
    print("="*70 + "\n")


def run_analysis(
    max_factors=None,
    start_date=None,
    end_date=None,
    factors_file='factors.txt',
    output_dir=None
):
    """Run the analysis"""
    
    max_factors = max_factors or MAX_FACTORS_PER_RUN
    output_dir = output_dir or OUTPUT_DIR
    
    # Get date range
    if not start_date or not end_date:
        start_date, end_date = get_date_range()
    
    print(f"Configuration:")
    print(f"  • Factors file:     {factors_file}")
    print(f"  • Date range:       {start_date} to {end_date}")
    print(f"  • Max factors:      {max_factors}")
    print(f"  • Output dir:       {output_dir}")
    print()
    
    # Verify factors file exists
    if not Path(factors_file).exists():
        print(f"❌ Error: {factors_file} not found")
        return False
    
    try:
        # Create analyzer
        analyzer = BTCFactorAnalyzer(
            factors_file=factors_file,
            output_dir=output_dir,
            start_date=start_date,
            end_date=end_date
        )
        
        # Run analysis
        results = analyzer.run_analysis(max_factors=max_factors)
        
        # Print results
        if results.get('success', True):
            print("\n✅ Analysis Complete!\n")
            
            print(f"📊 Results Summary:")
            print(f"  • Factors analyzed: {len(results.get('factors_analyzed', []))}")
            print(f"  • Factors failed:   {len(results.get('factors_failed', []))}")
            
            if results.get('factors_analyzed'):
                print(f"\n📈 Top Positive Correlations:")
                sorted_results = sorted(
                    results['factors_analyzed'],
                    key=lambda x: x['correlation'],
                    reverse=True
                )
                for item in sorted_results[:5]:
                    print(f"  • {item['factor']:30s}: {item['correlation']:7.4f}")
                
                print(f"\n📉 Top Negative Correlations:")
                for item in sorted_results[-5:]:
                    print(f"  • {item['factor']:30s}: {item['correlation']:7.4f}")
            
            print(f"\n📁 Output Files:")
            print(f"  • Directory:  {results.get('output_dir')}")
            print(f"  • Summary:    {results.get('summary_csv')}")
            print()
            
            return True
        else:
            print(f"❌ Error: {results.get('error', 'Unknown error')}")
            return False
    
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main entry point"""
    
    parser = argparse.ArgumentParser(
        description='Bitcoin Factor Analysis Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run.py                          # Run with default settings
  python run.py -f 20                    # Analyze 20 factors
  python run.py -s 2020-01-01 -e 2024-01-31  # Custom date range
  python run.py --factors custom_factors.txt -o custom_output
        """
    )
    
    parser.add_argument(
        '-f', '--factors',
        type=int,
        default=MAX_FACTORS_PER_RUN,
        help=f'Number of factors to analyze (default: {MAX_FACTORS_PER_RUN})'
    )
    
    parser.add_argument(
        '-s', '--start-date',
        type=str,
        default=None,
        help='Start date (YYYY-MM-DD) for analysis'
    )
    
    parser.add_argument(
        '-e', '--end-date',
        type=str,
        default=None,
        help='End date (YYYY-MM-DD) for analysis'
    )
    
    parser.add_argument(
        '--factors-file',
        type=str,
        default='factors.txt',
        help='Path to factors file (default: factors.txt)'
    )
    
    parser.add_argument(
        '-o', '--output',
        type=str,
        default=OUTPUT_DIR,
        help=f'Output directory (default: {OUTPUT_DIR})'
    )
    
    parser.add_argument(
        '--list-factors',
        action='store_true',
        help='List available factors and exit'
    )
    
    parser.add_argument(
        '--config',
        action='store_true',
        help='Show current configuration and exit'
    )
    
    args = parser.parse_args()
    
    print_banner()
    
    # Show configuration
    if args.config:
        print("Current Configuration:")
        print(f"  • START_DATE:          {START_DATE}")
        print(f"  • END_DATE:            {END_DATE}")
        print(f"  • MAX_FACTORS_PER_RUN: {MAX_FACTORS_PER_RUN}")
        print(f"  • OUTPUT_DIR:          {OUTPUT_DIR}")
        print(f"  • Available factors:   {len(get_custom_factors())}")
        print()
        return
    
    # List available factors
    if args.list_factors:
        factors = get_custom_factors()
        print(f"Available Factors ({len(factors)}):\n")
        for i, (name, ticker) in enumerate(sorted(factors.items()), 1):
            print(f"  {i:2d}. {name:40s} -> {ticker}")
        print()
        return
    
    # Run analysis
    success = run_analysis(
        max_factors=args.factors,
        start_date=args.start_date,
        end_date=args.end_date,
        factors_file=args.factors_file,
        output_dir=args.output
    )
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
