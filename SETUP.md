# Bitcoin Factor Analysis Tool - Setup & Installation Guide

## Quick Start (5 Minutes)

### Step 1: Install Python Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Run the Analysis
```bash
python run.py
```

Output will be in `BTC_Factor_Reports/` directory.

---

## Detailed Installation

### Prerequisites
- **Python 3.8+** (Check: `python --version`)
- **pip** (Python package manager)
- **Internet connection** (for data fetching)

### Option A: Standard Installation

#### 1. Clone/Download Repository
```bash
# Navigate to your project directory
cd C:\Users\moulo\Documents\Hobbies\BTCPredict
```

#### 2. Create Virtual Environment (Recommended)
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

#### 3. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### 4. Verify Installation
```bash
python -c "import yfinance, pandas, matplotlib; print('✓ All dependencies installed')"
```

### Option B: Docker Installation (Advanced)

Create a `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "run.py"]
```

Build and run:
```bash
docker build -t btc-analyzer .
docker run -v $(pwd)/output:/app/BTC_Factor_Reports btc-analyzer
```

---

## Running the Analysis

### Basic Usage
```bash
# Run with default settings (15 factors)
python run.py

# Run with specific number of factors
python run.py -f 30

# Run with custom date range
python run.py -s 2020-01-01 -e 2024-02-15

# Run with custom output directory
python run.py -o my_reports
```

### Command-Line Options
```bash
python run.py --help

Options:
  -f, --factors NUMBER       Number of factors to analyze
  -s, --start-date DATE      Start date (YYYY-MM-DD)
  -e, --end-date DATE        End date (YYYY-MM-DD)
  --factors-file FILE        Path to factors file
  -o, --output DIR          Output directory
  --list-factors            List available factors
  --config                  Show current configuration
```

### Examples
```bash
# Analyze top 10 factors for last year
python run.py -f 10 -s 2023-01-01

# Analyze all factors (very long-running)
python run.py -f 0  # Use 0 for unlimited

# List available factors
python run.py --list-factors

# Show current configuration
python run.py --config
```

---

## Configuration

### Edit `config.py`

The main configuration file controls all analysis parameters:

```python
# Change number of factors analyzed
MAX_FACTORS_PER_RUN = 15  # → Change to 30

# Change date range
START_DATE = '2022-01-01'  # → Change to '2020-01-01'
END_DATE = None             # → Change to '2024-02-15'

# Add/modify custom factors
CUSTOM_FACTORS = {
    'My Custom Factor': 'TICKER',
    ...
}
```

### Common Customizations

#### Add New Factor
```python
# In config.py, CUSTOM_FACTORS dictionary:
CUSTOM_FACTORS = {
    ...
    'Your Factor Name': 'TICKER_SYMBOL',  # Add this line
    ...
}

# Find ticker symbols on Yahoo Finance: https://finance.yahoo.com
```

#### Change Output Location
```python
OUTPUT_DIR = 'my_custom_reports'  # Or full path: 'C:/Reports/BTC'
```

#### Adjust Date Range
```python
START_DATE = '2020-01-01'  # 2 years earlier = longer analysis
MAX_FACTORS_PER_RUN = 30   # Analyze more factors
```

#### Change Visualization Settings
```python
CHART_DPI = 300            # Higher = better quality (slower)
NORMALIZATION_METHOD = 'zscore'  # Different normalization
SEABORN_STYLE = 'darkgrid' # Different chart style
```

---

## Troubleshooting

### Issue: `ModuleNotFoundError: No module named 'yfinance'`

**Solution:**
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Issue: `FileNotFoundError: factors.txt`

**Solution:**
Make sure `factors.txt` is in the same directory as `run.py`:
```bash
ls -la *.txt  # On Windows: dir *.txt
```

### Issue: "No data retrieved for [Factor]"

**Reasons:**
- Ticker symbol not found
- Factor delisted or renamed
- Market data unavailable

**Solution:**
```bash
# Check available factors
python run.py --list-factors

# Verify ticker on Yahoo Finance
# https://finance.yahoo.com/quote/TICKER_HERE

# Remove invalid factor from config.py
```

### Issue: "Network error" or timeout

**Causes:**
- Internet connection issue
- Yahoo Finance API rate limiting
- ISP blocking

**Solution:**
```bash
# Wait a few minutes and retry
sleep 300
python run.py

# Or reduce number of factors
python run.py -f 5
```

### Issue: "Insufficient data for [Factor]"

**Causes:**
- Factor too new (less than 20 days of history)
- Data gaps in the period

**Solution:**
- Use longer date range: `python run.py -s 2020-01-01`
- Skip this factor (add to config.py EXCLUDED_FACTORS)

### Issue: Low disk space warnings

**Causes:**
- PDF reports and chart images use ~10-50 MB per 20 factors

**Solution:**
```bash
# Reduce number of factors or date range
python run.py -f 5 -s 2023-01-01

# Or delete old reports
rm -rf BTC_Factor_Reports/*
```

---

## Advanced Usage

### Python Script Integration

```python
from btc_factor_analyzer import BTCFactorAnalyzer

# Custom analysis
analyzer = BTCFactorAnalyzer(
    factors_file='factors.txt',
    output_dir='reports',
    start_date='2021-01-01',
    end_date='2024-02-15'
)

results = analyzer.run_analysis(max_factors=20)

# Process results programmatically
for item in results['factors_analyzed']:
    if item['correlation'] > 0.5:
        print(f"Strong correlation: {item['factor']}")
```

### Working with Results

```python
import pandas as pd

# Load summary CSV
df = pd.read_csv('BTC_Factor_Reports/BTC_Correlation_Summary.csv')

# Filter strong correlations
strong = df[abs(df['Correlation']) > 0.5]
print(strong)

# Plot distribution
import matplotlib.pyplot as plt
plt.hist(df['Correlation'], bins=20)
plt.xlabel('Correlation with BTC')
plt.ylabel('Frequency')
plt.show()
```

### Batch Analysis

Create multiple analyses with different parameters:

```bash
# Analysis 1: Short-term (3 months)
python run.py -f 10 -s 2023-11-15 -e 2024-02-15 -o reports_recent

# Analysis 2: Long-term (3 years)
python run.py -f 10 -s 2021-01-01 -e 2024-02-15 -o reports_longterm

# Analysis 3: Crisis period
python run.py -f 10 -s 2022-01-01 -e 2022-12-31 -o reports_2022
```

### Custom Data Sources

To use alternative data providers (FRED API, Investing.com, etc.):

1. Extend `DataFetcher` class in `btc_factor_analyzer.py`:
```python
class CustomDataFetcher(DataFetcher):
    def fetch_from_fred(self, series_id: str):
        # Implement FRED API call
        pass
```

2. Update factor mapping:
```python
CUSTOM_FACTORS = {
    'Real GDP': ('FRED', 'A191RA1Q027SBEA'),
    ...
}
```

---

## Performance & Optimization

### Speed Tips

1. **Reduce number of factors** (biggest impact):
   ```bash
   python run.py -f 5  # Much faster than 30
   ```

2. **Use shorter date range**:
   ```bash
   python run.py -s 2023-01-01  # Faster than 2 years
   ```

3. **Disable chart generation** (edit config.py):
   ```python
   GENERATE_VISUALIZATIONS = False
   ```

4. **Run during off-peak hours** (avoid API rate limiting)

### Memory Usage

- ~100 MB for 2 years of daily data
- Each PDF report: 2-5 MB
- Charts cached in memory (released after report generation)

### Typical Runtimes

| Factors | Date Range | Approx Time |
|---------|-----------|-------------|
| 5       | 1 year    | 1 min       |
| 10      | 2 years   | 2 min       |
| 20      | 2 years   | 4 min       |
| 30      | 3 years   | 10+ min     |

---

## API Rate Limits

Yahoo Finance has rate limits:
- ~2,000 requests per hour per IP
- This tool makes 1 request per factor

**Mitigation:**
- Built-in caching prevents duplicate requests
- Add delay between runs if running frequently
- Use VPN if hitting limits

---

## Data Quality

### What's Checked

✓ Missing values (forward-filled up to 5 days)  
✓ Duplicates (removed)  
✓ Data alignment (common dates only)  
✓ Minimum data points (>20 required)  

### Known Limitations

- **No intraday data** (only daily closing prices)
- **Weekday-only BTC** (stocks don't trade weekends)
- **Survivorship bias** (only current factors)
- **Historical correlations** may not predict future

---

## Maintenance

### Regular Updates

```bash
# Update dependencies to latest versions
pip install --upgrade -r requirements.txt

# Keep factors.txt up to date with relevant factors
# Remove outdated or irrelevant factors
```

### Archival

```bash
# Archive old reports
tar -czf btc_reports_backup_2024-02.tar.gz BTC_Factor_Reports/

# Clean up old reports
rm -rf BTC_Factor_Reports/*
```

### Logging

Check `btc_analysis.log` for:
- Errors and warnings
- Data fetch failures
- Processing details

---

## FAQ

**Q: Can I analyze factors in real-time?**  
A: The current tool uses daily data. Real-time requires intraday data (not implemented).

**Q: How far back can I go?**  
A: Yahoo Finance has most data from 2010+. Some factors have less history.

**Q: Can I add my own factors?**  
A: Yes! Add to `CUSTOM_FACTORS` in config.py with a valid Yahoo Finance ticker.

**Q: Why are some factors missing data?**  
A: Ticker may be invalid, delisted, or too new. Check `btc_analysis.log`.

**Q: How do I interpret the correlation?**  
A: Read the PDF interpretation section for each factor. See README.md for guidance.

**Q: Can I schedule this to run automatically?**  
A: Yes! Use Windows Task Scheduler or cron job:
```bash
# Windows Task Scheduler task at 9 AM daily:
python C:\Path\to\run.py
```

---

## Support Resources

- **Code issues**: Check `btc_analysis.log` for detailed errors
- **Data issues**: Verify ticker on https://finance.yahoo.com
- **Questions**: See README.md for comprehensive documentation
- **Examples**: Run `python examples.py` for working code samples

---

## Version History

- **v1.0** (2024-02-15): Initial release
  - Factor extraction from markdown
  - PDF report generation
  - Correlation analysis
  - Summary statistics

---

**Last Updated**: 2024-02-15  
**Python Version**: 3.8+  
**License**: MIT
