import os
import time
import yfinance as yf
import matplotlib
# Use a non-interactive backend to avoid Tkinter-related errors when running
# in environments without a GUI or when matplotlib is used during shutdown.
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd

def btc_lagged_correlation_analysis(period="1y", shift_days=1, plot=False):
    """
    Docstring for btc_lagged_correlation_analysis
    
    :param period: Description
    :param shift_days: Description
    :param plot: Description
    
    This function performs a lagged correlation analysis between Bitcoin (BTC) and a wide range of financial assets, including other cryptocurrencies, stock indices, ETFs, sector-specific ETFs, thematic ETFs, international ETFs, and bonds/commodities. The analysis identifies which assets are most influenced by the previous day's BTC price movements.
    output: A DataFrame containing the top 3 assets most correlated with yesterday's BTC price, along with the period and shift days used in the analysis.
    """
    
    if period not in ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "3y", "5y", "10y"]:
        raise ValueError("Invalid period. Choose from: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 3y, 5y, 10y.")
    
    # 1. Define the 100+ Ticker List (Indices, Sectors, and ETFs)
    other_cryptos = ['ETH-USD', 'ADA-USD', 'XRP-USD', 'SOL-USD', 'DOGE-USD', 'LTC-USD', 'BCH-USD', 'LINK-USD', 'DOT-USD', 'UNI-USD', 'AVAX-USD', 'MATIC-USD', 'ATOM-USD', 'ALGO-USD', 'VET-USD', 'FIL-USD', 'TRX-USD', 'XLM-USD', 'THETA-USD', 'AAVE-USD', 'EOS-USD', 'MKR-USD', 'COMP-USD', 'SUSHI-USD', 'YFI-USD', 'CRV-USD', 'SNX-USD', 'ZRX-USD', 'REN-USD', 'BAL-USD', 'GRT-USD', '1INCH-USD', 'KNC-USD', 'LRC-USD', 'OCEAN-USD', 'UMA-USD', 'BAND-USD', 'SRM-USD', 'RUNE-USD', 'CRO-USD', 'FTT-USD', 'GNO-USD', 'HNT-USD', 'KAVA-USD', 'LUNA-USD', 'NEAR-USD', 'RAY-USD', 'SAND-USD', 'STX-USD', 'WAVES-USD', 'ZIL-USD']
    stock_indices = ['^GSPC', '^DJI', '^IXIC', '^FTSE', '^N225', '^HSI', '^BSESN', '^MXX', '^AXJO', '^GDAXI', '^FCHI', '^AORD', '^SSMI', '^IBEX', '^TA125', '^KLSE', '^NZ50', '^OMX', '^RTS', '^SSEC']
    etfs = ['SPY', 'QQQ', 'DIA', 'IWM', 'VTI', 'VOO', 'IVV', 'VEA', 'VWO', 'EFA', 'EEM', 'VUG', 'VTV', 'VBR', 'VUG', 'VOT', 'VXF', 'VXF', 'XLF', 'XLY', 'XLC', 'XLI', 'XLE', 'XLB', 'XLV', 'XLU', 'XLRE', 'XLC']
    sector_etfs = ['XLY', 'XLP', 'XLE', 'XLF', 'XLV', 'XLI', 'XLB', 'XLRE', 'XLK', 'XLU', 'XLC']
    thematic_etfs = ['ARKK', 'ARKG', 'ARKW', 'ARKF', 'ARKQ', 'TAN', 'LIT', 'ICLN', 'PBW', 'CLOU', 'SKYY', 'SOXX', 'IGV', 'CIBR', 'BOTZ', 'TAN', 'LIT', 'ICLN', 'PBW', 'CLOU', 'SKYY', 'SOXX', 'IGV', 'CIBR', 'BOTZ']
    international_etfs = ['EEM', 'VWO', 'EWZ', 'EFA', 'VEA', 'IEMG', 'SCZ', 'GXC', 'FXI', 'MCHI', 'EWJ', 'EWQ', 'EWG', 'EWC', 'EWA', 'EWY', 'EWT', 'INDA']
    bonds_commodities = ['TLT', 'GLD', 'SLV', 'USO', 'DBC', 'GSG', 'PDBC', 'BND', 'AGG', 'LQD', 'JNK', 'HYG', 'SHY', 'IEI', 'IEF', 'TLT', 'GLD', 'SLV', 'USO', 'DBC', 'GSG', 'PDBC', 'BND', 'AGG', 'LQD', 'JNK', 'HYG', 'SHY', 'IEI', 'IEF']

    all_tickers = ["BTC-USD"] + other_cryptos + stock_indices + etfs + sector_etfs + thematic_etfs + international_etfs + bonds_commodities

    # 2. Download Data (with chunking + retry to mitigate rate limits)
    print("Downloading data...")

    def chunked_download(tickers, period, chunk_size=20, max_retries=3, backoff=1.7):
        parts = []
        for i in range(0, len(tickers), chunk_size):
            batch = tickers[i : i + chunk_size]
            attempt = 0
            while attempt < max_retries:
                try:
                    out = yf.download(batch, period=period, threads=False)
                    if isinstance(out, pd.DataFrame):
                        # prefer the 'Close' column if present
                        if 'Close' in out.columns:
                            closes = out['Close']
                        else:
                            closes = out
                    else:
                        closes = pd.DataFrame(out)
                    parts.append(closes)
                    break
                except Exception as e:
                    attempt += 1
                    wait = backoff ** attempt
                    print(f"Download error for batch {batch}: {e} -- retry {attempt}/{max_retries} after {wait:.1f}s")
                    time.sleep(wait)
            else:
                print(f"Failed to download batch after {max_retries} attempts: {batch}")
        if not parts:
            return pd.DataFrame()
        combined = pd.concat(parts, axis=1)
        # flatten multiindex like ('Close', 'TICKER')
        if isinstance(combined.columns, pd.MultiIndex):
            if 'Close' in combined.columns.levels[0]:
                combined = combined['Close']
        if isinstance(combined, pd.Series):
            combined = combined.to_frame()
        # Remove columns that are all NaN (failed symbols)
        combined = combined.dropna(axis=1, how='all')
        return combined

    data = chunked_download(all_tickers, period=period)

    # 3. Ensure BTC present
    if data.empty or 'BTC-USD' not in data.columns:
        print("Error: BTC-USD not available in downloaded data for this period. Skipping.")
        return pd.DataFrame(columns=['Ticker', 'Correlation', 'period', 'shift_days'])

    # 4. Calculate Daily Returns
    returns = data.pct_change(fill_method=None).dropna()

    # Avoid DataFrame fragmentation by concatenating the lagged series
    btc_lagged = returns['BTC-USD'].shift(shift_days).rename('BTC_Lagged')
    returns = pd.concat([returns, btc_lagged], axis=1).dropna()

    # 5. Calculate Correlation with the Lagged BTC
    # We compare Today's Index Return with Yesterday's BTC Return
    lagged_correlations = returns.corr()['BTC_Lagged'].drop(['BTC-USD', 'BTC_Lagged'])

    # 6. Find the "Top 20" most influenced by yesterday's BTC
    top_lagged = lagged_correlations.sort_values(ascending=False).head(20)

    print("\n--- Top 20 Assets Most Correlated with YESTERDAY'S BTC ---")
    print(top_lagged)
    
    # save output to a text file
    # if not os.path.exists("laggedCorrelationAnalysis"):
    #     os.makedirs("laggedCorrelationAnalysis")
    # with open("laggedCorrelationAnalysis/lagged_correlation_output_"+period+"+ sh="+str(shift_days)+".txt", "w") as f:
    #     f.write("--- Top 20 Assets Most Correlated with YESTERDAY'S BTC ---\n")
    #     f.write(top_lagged.to_string())

    # 7. Visualization
    plt.figure(figsize=(12, 8))
    top_lagged.plot(kind='barh', color='skyblue')
    plt.title("Indices Most Influenced by Yesterday's BTC Price (Lagged Correlation)")
    plt.xlabel("Correlation Coefficient")
    plt.grid(axis='x', linestyle='--', alpha=0.7)
    plt.tight_layout()
    # save the plot and ensure figures are closed to free resources
    # try:
    #     plt.savefig("laggedCorrelationAnalysis/lagged_correlation_plot_"+period+"+ sh="+str(shift_days)+".png")
    # finally:
    #    plt.close('all')
        
    if plot:
        plt.show()

    # top 3 most influenced assets -> return as a DataFrame
    top_3 = top_lagged.head(3).reset_index()
    top_3.columns = ['Ticker', 'Correlation']
    top_3['period'] = period
    top_3['shift_days'] = shift_days
    return top_3

def main():
    periods = ["1mo", "3mo", "6mo", "1y", "2y", "3y"]
    shift_days = 1  # You can adjust this to 2, 3, etc. for different lags
    # prepare output directories and rotate existing summary into OutputLaggedCorrelationAnalysis/Old
    out_dir = "OutputLaggedCorrelationAnalysis"
    old_dir = os.path.join(out_dir, "Old")
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    if not os.path.exists(old_dir):
        os.makedirs(old_dir)

    summary_path = os.path.join(out_dir, "lagged_correlation_output_summary.txt")
    if os.path.exists(summary_path):
        timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
        dest = os.path.join(old_dir, f"lagged_correlation_output_summary_{timestamp}.txt")
        os.rename(summary_path, dest)

    with open(summary_path, "w") as f:
        f.write("--- Lagged Correlation Analysis Summary ---\n")
                
    for period in periods:
        for i in range(1, 8):  # Analyze for shift of 1, 2, ..., 7 days
            print(f"\nAnalyzing period: {period} with shift of {i} day(s)...")
            # create txt file to store the output of each analysis
            
            with open("OutputLaggedCorrelationAnalysis/lagged_correlation_output_summary.txt", "a") as f:
                f.write(f"\n\n--- Analysis for Period: {period} with Shift of {i} day(s) ---\n")
            top_3 = btc_lagged_correlation_analysis(period=period, shift_days=i)
            with open("OutputLaggedCorrelationAnalysis/lagged_correlation_output_summary.txt", "a") as f:
                f.write(top_3.to_string())
                
    # return summary_path file containing all the results for decision engine to read
    return summary_path
        
if __name__ == "__main__":
    main()
