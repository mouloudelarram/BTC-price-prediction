# Bitcoin Factor Analysis Tool

A comprehensive Python program that automatically fetches historical data for Bitcoin and various economic/financial factors, generates professional PDF reports with visualizations, and analyzes correlations.

## Overview

This tool:
1. **Extracts factors** from your `factors.txt` file
2. **Fetches historical data** for BTC and each factor from Yahoo Finance and other sources
3. **Aligns data** on common dates and preprocesses for analysis
4. **Creates visualizations** showing BTC vs factor evolution
5. **Calculates statistics** including Pearson and Spearman correlations
6. **Generates PDF reports** for each factor with professional layouts
7. **Creates a summary** CSV and PDF with all correlation coefficients ranked

## Features

✅ **Fully Automated** - One command processes all factors  
✅ **Professional Visualizations** - 4-panel charts with normalized plots, scatter plots, rolling correlation, and statistics  
✅ **Statistical Analysis** - Pearson/Spearman correlations, p-values, summary statistics  
✅ **PDF Reports** - Professional, readable reports for each factor  
✅ **Summary Rankings** - CSV and PDF with all factors ranked by correlation  
✅ **Error Handling** - Graceful handling of missing data, API failures  
✅ **Logging** - Detailed logging to file and console  
✅ **Caching** - Efficient data reuse to minimize API calls  

## Installation

### 1. Clone/Create Project Directory
```bash
cd C:\Users\moulo\Documents\Hobbies\BTCPredict
```

### 2. Install Python Dependencies
```bash
pip install -r requirements.txt
```

If you prefer to use a virtual environment:
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## Usage

### Basic Usage
```python
python btc_factor_analyzer.py
```

This will:
- Read factors from `factors.txt`
- Analyze the first 15 factors (configurable)
- Create reports in `BTC_Factor_Reports/` directory
- Generate PDFs, charts, and a summary CSV

### Advanced Usage - Custom Script

```python
from btc_factor_analyzer import BTCFactorAnalyzer

# Create analyzer with custom parameters
analyzer = BTCFactorAnalyzer(
    factors_file='factors.txt',
    output_dir='BTC_Factor_Reports',
    start_date='2020-01-01',  # Custom start date
    end_date='2024-02-15'      # Custom end date
)

# Run analysis
results = analyzer.run_analysis(max_factors=20)

# Access results
for item in results['factors_analyzed']:
    print(f"{item['factor']}: {item['correlation']:.4f}")
```

### Configuration Options

In `btc_factor_analyzer.py`, modify the `main()` function:

```python
analyzer = BTCFactorAnalyzer(
    factors_file=str(factors_file),        # Path to factors.txt
    output_dir=str(output_dir),             # Output directory for reports
    start_date='2022-01-01',                # Historical data start date
    end_date=None                           # End date (None = today)
)

results = analyzer.run_analysis(max_factors=15)  # Limit factors to analyze
```

## Output Files

### Directory Structure
```
BTC_Factor_Reports/
├── BTC_Correlation_Summary.csv              # All factors ranked by correlation
├── BTC_Correlation_Summary.pdf              # Summary PDF with rankings
├── BTC_vs_S&P_500.pdf                      # Individual factor report
├── BTC_vs_Gold_(XAU_USD).pdf
├── BTC_vs_NASDAQ_100.pdf
├── ... (one PDF per factor)
├── chart_S&P_500.png                       # Supporting chart images
├── chart_Gold_(XAU_USD).png
└── ... (one chart per factor)
```

### CSV Summary Format
```csv
Factor,Correlation,P-Value,Data Points,PDF
S&P 500,0.6234,0.0001,730,/path/BTC_vs_S&P_500.pdf
Gold (XAU/USD),0.5421,0.0003,730,/path/BTC_vs_Gold_(XAU_USD).pdf
...
```

### PDF Report Contents

Each PDF includes:
- **Title & Metadata** - Factor name, analysis period, generation date
- **Multi-Panel Chart**:
  - Normalized price evolution (BTC vs Factor)
  - Scatter plot with trend line
  - 30-day rolling correlation
  - Statistical summary box
- **Statistics Table**:
  - Correlation coefficients (Pearson & Spearman)
  - P-values and data points
  - BTC price statistics (mean, std dev, min, max)
  - Factor statistics
- **Interpretation** - English explanation of correlation strength

## Supported Factors

The tool includes built-in support for 60+ factors:

**Stock Indices**: S&P 500, NASDAQ 100, Dow Jones, DAX, FTSE 100, Nikkei 225, etc.  
**Bonds & Rates**: 10-Year Treasury Yield, 2-Year Yield, Fed Funds Rate, etc.  
**Currencies**: USD Index (DXY), EUR/USD, GBP/USD, USD/JPY, etc.  
**Commodities**: Gold, Crude Oil (WTI), Copper, Natural Gas, etc.  
**Crypto**: Ethereum (ETH), Binance Coin (BNB), Ripple (XRP), etc.  
**Volatility**: VIX, MOVE Index, etc.  

### Adding Custom Factors

Edit the `TICKER_MAPPING` dictionary in `DataFetcher` class:

```python
TICKER_MAPPING = {
    ...
    'Your Factor Name': 'TICKER_SYMBOL',  # Add your factor here
    ...
}
```

For example:
```python
'Brazilian Real/USD': 'BRL=F',
'Russell 2000': '^RUT',
'Palladium': 'PA=F',
```

## Data Sources

| Data Type | Source | Notes |
|-----------|--------|-------|
| BTC & Crypto Prices | Yahoo Finance | Free API, reliable, minute to daily data |
| Stock Indices | Yahoo Finance | Real-time data available |
| Bond Yields | Yahoo Finance | Treasury yields, corporate spreads |
| Forex | Yahoo Finance | Major currency pairs |
| Commodities | Yahoo Finance | Futures prices, real-time |
| Volatility | Yahoo Finance | VIX, MOVE index |

**API Limits**: Yahoo Finance has rate limiting. The tool includes built-in caching to minimize requests.

## Data Handling

### Alignment
- All data is aligned to common trading dates (no BTC trades weekends, so stocks are interpolated)
- Missing values forward-filled up to 5 days
- Records with NaN values dropped

### Quality Checks
- Duplicates removed
- Empty datasets skipped with warnings
- Correlation only calculated with >10 data points

### Edge Cases
- **No data for factor**: Logged as warning, analysis skipped
- **Insufficient overlap**: Factor marked as failed
- **API errors**: Gracefully handled, next factor processed
- **Network issues**: Automatic retry (1 attempt, can be configured)

## Statistical Methods

### Correlation Metrics
- **Pearson Correlation**: Linear relationship, parametric
- **Spearman Correlation**: Rank-based relationship, non-parametric
- **P-value**: Statistical significance (p < 0.05 = significant)
- **Rolling Correlation**: 30-day window correlation over time

### Returns Calculation
- Daily log returns: `ln(P_t / P_{t-1})`
- Correlation of returns (not prices) for better statistical properties

## Performance

- **Data Fetching**: ~1-2 seconds per factor
- **Chart Generation**: ~1-2 seconds per factor
- **PDF Creation**: ~0.5-1 second per report
- **Total Time**: ~15 factors in 2-3 minutes
- **Memory Usage**: Minimal, ~100-200 MB for 2 years of daily data

## Troubleshooting

### Issue: "No module named 'yfinance'"
**Solution**: Install dependencies:
```bash
pip install -r requirements.txt
```

### Issue: "No data retrieved for [Factor]"
**Cause**: Ticker not found or delisted  
**Solution**: 
- Verify ticker symbol in `TICKER_MAPPING`
- Check if ticker is valid on Yahoo Finance
- Ensure market is open (weekdays)

### Issue: Empty CSV summary
**Cause**: All factors failed to fetch  
**Solution**:
- Check internet connection
- Verify factor names match TICKER_MAPPING
- Check logs in `btc_analysis.log`

### Issue: Slow performance
**Cause**: API rate limiting  
**Solution**:
- Reduce `max_factors` parameter
- Run in off-hours (Yahoo Finance less congested)
- Increase time between runs

## Example Results

```
==============================================================
ANALYSIS RESULTS SUMMARY
==============================================================

Successfully analyzed factors:
  • S&P 500                                | Correlation:   0.6234
  • NASDAQ 100                            | Correlation:   0.6891
  • Gold (XAU/USD)                        | Correlation:   0.5421
  • Ethereum (ETH)                        | Correlation:   0.9123
  • DXY (US Dollar Index)                 | Correlation:  -0.4532
  • 10-Year Treasury Yield                | Correlation:  -0.3821
  • Crude Oil (WTI)                       | Correlation:   0.4123
  • VIX (CBOE Volatility Index)           | Correlation:  -0.5234
  ...

Failed to analyze:
  • Your Factor Name (no ticker mapping)

Output files saved to: C:\Users\moulo\Documents\Hobbies\BTCPredict\BTC_Factor_Reports
Summary report: C:\Users\moulo\Documents\Hobbies\BTCPredict\BTC_Factor_Reports\BTC_Correlation_Summary.csv
==============================================================
```

## Interpretation Guide

### Correlation Strength
- **0.70 to 1.00**: Very strong relationship
- **0.50 to 0.69**: Strong relationship
- **0.30 to 0.49**: Moderate relationship
- **0.10 to 0.29**: Weak relationship
- **0.00 to 0.09**: Very weak/no relationship

### Positive vs Negative
- **Positive (+)**: BTC rises when factor rises
- **Negative (-)**: BTC rises when factor falls (inverse relationship)

### P-Value Significance
- **p < 0.05**: Statistically significant (reliable relationship)
- **p ≥ 0.05**: Not statistically significant (could be random)

## Advanced Topics

### Custom Data Source Integration

To add a custom data source, modify `DataFetcher`:

```python
def fetch_custom_factor(self, factor_name: str, api_key: str = None) -> Optional[pd.DataFrame]:
    """Fetch from your custom API"""
    # Implement your API call
    # Return DataFrame with 'Date' and 'Close' columns
    pass
```

### Extending Analysis

Create subclasses for advanced analysis:

```python
class AdvancedAnalyzer(BTCFactorAnalyzer):
    def calculate_beta(self, btc_returns, factor_returns):
        """Calculate BTC beta vs factor"""
        covariance = np.cov(btc_returns, factor_returns)[0][1]
        variance = np.var(factor_returns)
        return covariance / variance
```

## Limitations & Considerations

1. **Historical correlation ≠ Future correlation** - Past relationships may not hold
2. **Survivorship bias** - Only analyzes factors with current data
3. **Non-stationarity** - Correlation can change over time
4. **Outliers** - Extreme events can skew results
5. **Causation** - Correlation does not imply causation
6. **Multiple comparisons** - Many tests increase false positive risk
7. **Data quality** - Dependent on Yahoo Finance data accuracy
8. **Lag effects** - Some relationships may have time lags not captured

## License

MIT License - Use freely for personal or commercial projects

## Contributing

To improve this tool:
1. Add new data sources to `DataFetcher.TICKER_MAPPING`
2. Enhance visualizations in `ReportGenerator.create_visualization()`
3. Add new statistical metrics
4. Improve PDF layouts
5. Optimize data fetching

## Support

For issues or questions:
1. Check `btc_analysis.log` for detailed error messages
2. Review the Troubleshooting section above
3. Verify factor names and ticker symbols
4. Check internet connection and API availability

## Future Enhancements

Potential additions:
- [ ] Support for alternative data sources (FRED API, Investing.com, etc.)
- [ ] Machine learning model for factor importance
- [ ] Real-time data fetching and reporting
- [ ] Interactive HTML dashboard instead of static PDFs
- [ ] Lagged correlation analysis
- [ ] Multi-period analysis (daily, weekly, monthly)
- [ ] Causality testing (Granger causality)
- [ ] Factor weighting and portfolio optimization
- [ ] Risk metrics (Value at Risk, Sharpe Ratio)
- [ ] Sentiment analysis from news and social media

---

**Version**: 1.0  
**Last Updated**: 2024-02-15  
**Python Version**: 3.8+
#   B T C - p r i c e - p r e d i c t i o n 
 
 
