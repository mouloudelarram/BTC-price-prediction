# Architecture & Workflow Diagram

## Overall System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                  BITCOIN FACTOR ANALYSIS TOOL                   │
└─────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────┐
│                         INPUT SOURCES                                │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────────────┐      ┌──────────────────┐                    │
│  │  factors.txt     │      │  config.py       │                    │
│  │                  │      │                  │                    │
│  │ • Stock Indices  │      │ • Date Range     │                    │
│  │ • Bonds & Rates  │      │ • Max Factors    │                    │
│  │ • Currencies     │      │ • Factor Tickers │                    │
│  │ • Commodities    │      │ • Output Dir     │                    │
│  │ • Cryptos        │      │ • Chart Settings │                    │
│  │ • 300+ Factors   │      │ • Analysis Opts  │                    │
│  └──────────────────┘      └──────────────────┘                    │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌──────────────────────────────────────────────────────────────────────┐
│                      BTCFACTORANALYZER                               │
│                    (Main Orchestrator)                               │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ 1. FACTOREXTRACTOR: Parse factors.txt                      │   │
│  │    • Regex pattern matching                                │   │
│  │    • Deduplicate factors                                  │   │
│  │    • Return: List of 300+ factor names                   │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                      │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ 2. DATAFETCHER: Fetch historical data                      │   │
│  │    • Map factor names to Yahoo Finance tickers            │   │
│  │    • Fetch BTC data (BTC-USD)                            │   │
│  │    • Fetch factor data (one per factor)                  │   │
│  │    • Cache results to minimize API calls                 │   │
│  │    • Return: DataFrame with Date & Close columns         │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                      │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ 3. DATAPROCESSOR: Align & process data                     │   │
│  │    • Merge BTC and factor data on common dates            │   │
│  │    • Handle missing values (forward-fill)                │   │
│  │    • Remove duplicates and NaN values                    │   │
│  │    • Calculate Pearson & Spearman correlations          │   │
│  │    • Calculate p-values                                 │   │
│  │    • Return: Statistics dictionary                       │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                      │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ 4. REPORTGENERATOR: Create visualizations & PDFs           │   │
│  │    • Create 4-panel matplotlib chart                      │   │
│  │    • Normalize price data                                │   │
│  │    • Plot scatter with trend line                        │   │
│  │    • Calculate 30-day rolling correlation                │   │
│  │    • Save chart as PNG image                            │   │
│  │    • Generate professional PDF report                   │   │
│  │    • Create summary CSV and ranking PDF                 │   │
│  │    • Return: File paths & metadata                       │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                      │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ 5. LOOP: For each factor (up to MAX_FACTORS_PER_RUN)       │   │
│  │    ├─ Fetch factor data (step 2)                         │   │
│  │    ├─ Align with BTC data (step 3)                       │   │
│  │    ├─ Calculate statistics (step 3)                      │   │
│  │    ├─ Create visualization (step 4)                      │   │
│  │    ├─ Generate PDF report (step 4)                       │   │
│  │    ├─ Store results in summary                           │   │
│  │    └─ Continue to next factor                            │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌──────────────────────────────────────────────────────────────────────┐
│                       OUTPUT FILES                                   │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  BTC_Factor_Reports/                                               │
│  │                                                                  │
│  ├─ BTC_Correlation_Summary.csv                                   │
│  │  └─ Factor | Correlation | P-Value | Data Points | PDF Path   │
│  │                                                                  │
│  ├─ BTC_Correlation_Summary.pdf                                   │
│  │  └─ Table with all factors ranked by correlation              │
│  │                                                                  │
│  ├─ BTC_vs_S&P_500.pdf                                            │
│  │  ├─ 4-panel chart                                             │
│  │  ├─ Statistics table                                          │
│  │  └─ Interpretation text                                       │
│  │                                                                  │
│  ├─ BTC_vs_Gold_(XAU_USD).pdf                                     │
│  │  └─ (one per factor analyzed)                                 │
│  │                                                                  │
│  ├─ chart_S&P_500.png                                             │
│  │  └─ High-resolution chart image                               │
│  │                                                                  │
│  └─ chart_Gold_(XAU_USD).png                                       │
│     └─ (one per factor analyzed)                                  │
│                                                                      │
│  Plus logging:                                                      │
│  └─ btc_analysis.log                                               │
│     └─ Detailed execution log (timestamps, errors, progress)      │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

## Data Flow Diagram

```
                          ┌─────────────────┐
                          │   factors.txt   │
                          └────────┬────────┘
                                   │
                                   ▼
                    ┌──────────────────────────────┐
                    │   FactorExtractor.extract()  │
                    │                              │
                    │ Regex parse → Deduplicate   │
                    └────────────┬─────────────────┘
                                 │
                    ┌────────────┴────────────┐
                    │  300+ Factor Names     │
                    │  (S&P 500, Gold, etc)  │
                    └────────────┬────────────┘
                                 │
                    ┌────────────┴────────────────────────────┐
                    │  For each factor (filtered to MAX_N):   │
                    │                                         │
        ┌──────────┴──────────┐                              │
        │                     │                              │
        ▼                     ▼                              │
  ┌──────────────┐      ┌──────────────┐                    │
  │ Fetch BTC    │      │ Fetch Factor │  (map ticker)      │
  │ Data         │      │ Data         │                    │
  │ BTC-USD      │      │ (^GSPC, etc) │                    │
  └──────┬───────┘      └──────┬───────┘                    │
         │                     │                            │
         │                ┌────┴────────────────┐           │
         │                │ Data Fetching Errors│           │
         │                │ → Log & Skip Factor │           │
         │                └────────────────────┘            │
         │                     │                            │
         └────────┬────────────┘                            │
                  │                                         │
    ┌─────────────▼──────────────┐                         │
    │ BTC DataFrame              │                         │
    │ Date  | Close_BTC          │                         │
    │ 2022  |  19000             │                         │
    │ ...   |  ...               │                         │
    │ 2024  |  40000             │                         │
    └─────────────┬──────────────┘                         │
                  │                                         │
    ┌─────────────▼──────────────┐                         │
    │ Factor DataFrame           │                         │
    │ Date  | Close_Factor       │                         │
    │ 2022  |  4000              │                         │
    │ ...   |  ...               │                         │
    │ 2024  |  5000              │                         │
    └─────────────┬──────────────┘                         │
                  │                                         │
    ┌─────────────▼──────────────────────┐                │
    │ DataProcessor.align_data()         │                │
    │                                    │                │
    │ • Merge on Date (inner join)      │                │
    │ • Forward-fill missing values     │                │
    │ • Drop NaNs                       │                │
    │ • Validate minimum records        │                │
    └─────────────┬──────────────────────┘                │
                  │                                       │
    ┌─────────────▼──────────────────────┐                │
    │ Aligned DataFrame                  │                │
    │ Date | Close_BTC | Close_Factor    │                │
    │ ...  |  ...      |  ...            │                │
    │ 500+ records     | Common dates    │                │
    └─────────────┬──────────────────────┘                │
                  │                                       │
    ┌─────────────▼──────────────────────┐                │
    │ DataProcessor.calculate_stats()    │                │
    │                                    │                │
    │ • Calculate daily returns         │                │
    │ • Pearson correlation             │                │
    │ • Spearman correlation            │                │
    │ • P-values                        │                │
    │ • Descriptive statistics          │                │
    └─────────────┬──────────────────────┘                │
                  │                                       │
    ┌─────────────▼──────────────────────┐                │
    │ Statistics Dictionary              │                │
    │ {                                  │                │
    │   'correlation': 0.6234,           │                │
    │   'p_value': 0.0001,              │                │
    │   'btc_mean': 25000,              │                │
    │   ...                             │                │
    │ }                                  │                │
    └─────────────┬──────────────────────┘                │
                  │                                       │
    ┌─────────────▼──────────────────────┐                │
    │ ReportGenerator.create_viz()       │                │
    │                                    │                │
    │ • Normalize prices [0, 1]         │                │
    │ • Plot 4 panels:                  │                │
    │   1. Normalized evolution         │                │
    │   2. Scatter + trend              │                │
    │   3. Rolling correlation          │                │
    │   4. Statistics box               │                │
    │ • Save as PNG (150 DPI)           │                │
    └─────────────┬──────────────────────┘                │
                  │                                       │
    ┌─────────────▼──────────────────────┐                │
    │ Chart PNG File                     │                │
    │ chart_S&P_500.png (500 KB)         │                │
    └─────────────┬──────────────────────┘                │
                  │                                       │
    ┌─────────────▼──────────────────────┐                │
    │ ReportGenerator.create_pdf()       │                │
    │                                    │                │
    │ • Generate reportlab document     │                │
    │ • Add title & metadata            │                │
    │ • Embed chart image               │                │
    │ • Create statistics table         │                │
    │ • Write interpretation            │                │
    │ • Save as PDF (2-3 pages)         │                │
    └─────────────┬──────────────────────┘                │
                  │                                       │
    ┌─────────────▼──────────────────────┐                │
    │ PDF Report File                    │                │
    │ BTC_vs_S&P_500.pdf (200 KB)        │                │
    │                                    │                │
    │ Pages:                             │                │
    │ [1] Title + 4-panel chart          │                │
    │ [2] Statistics table + interpret   │                │
    └─────────────┬──────────────────────┘                │
                  │                                       │
    └──────────────┬─────────────────────────────────────┘
                   │
         (Repeat for next factor)
                   │
                   ▼
    ┌──────────────────────────────────┐
    │ All Results Collected             │
    │                                  │
    │ {                                │
    │   'factors_analyzed': [         │
    │     {                           │
    │       'factor': 'S&P 500',       │
    │       'correlation': 0.6234,     │
    │       'p_value': 0.0001,         │
    │       'pdf': '...pdf'            │
    │     },                           │
    │     ...                          │
    │   ]                              │
    │ }                                │
    └────────┬─────────────────────────┘
             │
    ┌────────▼──────────────────────────┐
    │ ReportGenerator.create_summary()  │
    │                                   │
    │ • Create CSV with all factors    │
    │ • Sort by correlation            │
    │ • Create summary PDF (ranking)   │
    └────────┬──────────────────────────┘
             │
    ┌────────▼──────────────────────────┐
    │ Final Output Files:                │
    │                                   │
    │ BTC_Factor_Reports/              │
    │ ├─ Summary.csv                   │
    │ ├─ Summary.pdf                   │
    │ ├─ BTC_vs_S&P_500.pdf           │
    │ ├─ chart_S&P_500.png            │
    │ ├─ BTC_vs_Gold.pdf              │
    │ ├─ chart_Gold.png               │
    │ └─ ... (15-30 factors)           │
    │                                   │
    │ btc_analysis.log                 │
    └────────────────────────────────────┘
```

## Class Interaction Diagram

```
┌──────────────────────────────────────────────────────────────┐
│                   BTCFactorAnalyzer                          │
│                  (Main Orchestrator)                         │
│                                                              │
│  ┌─ __init__()                                             │
│  │   ├─ Creates FactorExtractor                           │
│  │   ├─ Creates DataFetcher                               │
│  │   ├─ Creates DataProcessor                             │
│  │   └─ Creates ReportGenerator                           │
│  │                                                          │
│  └─ run_analysis()                                          │
│     └─ Orchestrates the analysis pipeline                 │
│                                                              │
│     Step 1: factors = extractor.extract_factors()         │
│            ▼                                               │
│     Step 2: btc_data = fetcher.fetch_btc_data()           │
│            ▼                                               │
│     Step 3: FOR each factor in factors:                   │
│            │                                               │
│            ├─ factor_data = fetcher.fetch_factor_data()   │
│            │  ▼                                            │
│            ├─ aligned_data = processor.align_data()       │
│            │  ▼                                            │
│            ├─ stats = processor.calculate_statistics()    │
│            │  ▼                                            │
│            ├─ chart = report_gen.create_visualization()   │
│            │  ▼                                            │
│            ├─ pdf = report_gen.create_pdf_report()        │
│            │  ▼                                            │
│            └─ Store result in summary_data                │
│                                                              │
│     Step 4: summary_csv = report_gen.create_summary()     │
│                                                              │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────┐
│     FactorExtractor              │
│                                  │
│ - file_path: str                │
│ - factors: List[str]            │
│                                  │
│ + extract_factors()             │
│   → List[str] (300+ factors)    │
│                                  │
│ + _get_default_factors()        │
│   → List[str]                   │
└──────────────────────────────────┘

┌──────────────────────────────────┐
│      DataFetcher                 │
│                                  │
│ - start_date: str               │
│ - end_date: str                 │
│ - data_cache: Dict              │
│ - TICKER_MAPPING: Dict (60+)    │
│                                  │
│ + fetch_btc_data()              │
│   → pd.DataFrame                │
│                                  │
│ + fetch_factor_data(name)       │
│   → pd.DataFrame or None        │
└──────────────────────────────────┘

┌──────────────────────────────────┐
│     DataProcessor                │
│                                  │
│ + align_data(btc_df, factor_df) │
│   → (aligned_df, aligned_df)    │
│                                  │
│ + calculate_statistics()         │
│   → Dict {                       │
│       'correlation': float,     │
│       'p_value': float,         │
│       'btc_mean': float,        │
│       ...                       │
│     }                            │
└──────────────────────────────────┘

┌────────────────────────────────────┐
│     ReportGenerator                │
│                                    │
│ - output_dir: Path               │
│ - summary_data: List[Dict]       │
│                                    │
│ + create_visualization()          │
│   → str (PNG file path)           │
│                                    │
│ + create_pdf_report()             │
│   → str (PDF file path)           │
│                                    │
│ + create_summary_report()         │
│   → str (CSV file path)           │
│                                    │
│ + _create_summary_pdf()           │
│   → str (PDF file path)           │
└────────────────────────────────────┘
```

## Execution Flow Timeline

```
Time    Action                          Component           Output
────    ──────────────────────────────  ────────────────    ──────────────────
T+0s    Parse command-line arguments   run.py              Parsed args
T+1s    Initialize BTCFactorAnalyzer   __init__            Analyzer ready
T+2s    Extract factors from factors.txt FactorExtractor   300+ factors
T+3s    Fetch Bitcoin data             DataFetcher         BTC DataFrame
T+4s    ─────────────────────────────────────────────────────────────
        Loop: For each of 15 factors:
T+5s      Fetch S&P 500 data          DataFetcher         Factor DataFrame
T+6s      Align dates with BTC        DataProcessor       730 aligned records
T+7s      Calculate correlation       DataProcessor       Correlation: 0.6234
T+8s      Create visualization        ReportGenerator     PNG chart
T+9s      Create PDF report           ReportGenerator     BTC_vs_S&P_500.pdf
T+10s   ─────────────────────────────────────────────────────────────
T+11s     Fetch Gold data             DataFetcher         Factor DataFrame
T+12s     Align with BTC              DataProcessor       730 records
T+13s     Calculate correlation       DataProcessor       Correlation: 0.5421
T+14s     Create visualization        ReportGenerator     PNG chart
T+15s     Create PDF report           ReportGenerator     BTC_vs_Gold.pdf
T+16s   ... (repeat for 13 more factors)
T+45s   ─────────────────────────────────────────────────────────────
T+46s   Create summary CSV            ReportGenerator     Summary.csv
T+47s   Create summary PDF            ReportGenerator     Summary.pdf
T+48s   Report completion             run.py              ✓ Complete
        Display results summary        run.py              15 analyzed, 0 failed
────────────────────────────────────────────────────────────────────────
Total: ~48 seconds for 15 factors (2-3x faster with caching)
```

## Configuration Impact Diagram

```
┌─────────────────────────────────────────────────────────┐
│                   config.py Settings                    │
└─────────────────────────────────────────────────────────┘
         │
         ├─ START_DATE / END_DATE
         │  └─ Affects: Date range for analysis
         │     Impact: More data = longer analysis
         │
         ├─ MAX_FACTORS_PER_RUN
         │  └─ Affects: Number of factors analyzed
         │     Impact: Linear time increase
         │
         ├─ CUSTOM_FACTORS (Ticker Mapping)
         │  └─ Affects: Which factors are available
         │     Impact: Failed factors if ticker invalid
         │
         ├─ OUTPUT_DIR
         │  └─ Affects: Where PDFs are saved
         │     Impact: Directory structure
         │
         ├─ CHART_DPI
         │  └─ Affects: Chart image quality
         │     Impact: File size & visual quality
         │
         ├─ SEABORN_STYLE
         │  └─ Affects: Chart appearance
         │     Impact: Visual presentation
         │
         ├─ NORMALIZATION_METHOD
         │  └─ Affects: How prices are scaled
         │     Impact: Visualization interpretation
         │
         ├─ MIN_DATA_POINTS
         │  └─ Affects: Minimum records required
         │     Impact: Factor rejection threshold
         │
         ├─ ROLLING_WINDOW
         │  └─ Affects: Rolling correlation window
         │     Impact: Smoothing/responsiveness
         │
         └─ LOG_LEVEL
            └─ Affects: Logging verbosity
               Impact: Detail in btc_analysis.log
```

---

This architecture is designed to be:
- **Modular**: Each class has a single responsibility
- **Extensible**: Easy to add new data sources or analysis methods
- **Robust**: Comprehensive error handling throughout
- **Efficient**: Caching, vectorized operations, parallel potential
- **Maintainable**: Clear code structure and documentation
