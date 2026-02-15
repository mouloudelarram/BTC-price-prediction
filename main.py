import yfinance as yf
from datetime import datetime
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os

# Download BTC data since 2010
btc_data = yf.download('BTC-USD', start='2010-01-01', end=datetime.now().strftime('%Y-%m-%d'))
eth_data = yf.download('ETH-USD', start='2015-01-01', end=datetime.now().strftime('%Y-%m-%d'))


# Create the plot for BTC price
def plot_btc_price(data):
    plt.figure(figsize=(14, 7))
    plt.plot(data.index, data['Close'], linewidth=2, color='#F7931A')

    plt.title('Bitcoin Price Since 2010', fontsize=16, fontweight='bold')
    plt.xlabel('Year', fontsize=12)
    plt.ylabel('Price (USD)', fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    # Display the plot
    plt.show()
# Example usage:
# plot_btc_price(btc_data)

# cretae a function that take in input two values (ex: btc data and eth data) and plot them on the same graph with different colors and labels
def plot_crypto_prices(crypto1_data, crypto2_data, crypto1_label='Crypto 1', crypto2_label='Crypto 2'):
    plt.figure(figsize=(14, 7))
    plt.plot(crypto1_data.index, crypto1_data['Close'], linewidth=2, label=crypto1_label)
    plt.plot(crypto2_data.index, crypto2_data['Close'], linewidth=2, label=crypto2_label)

    plt.title(f'{crypto1_label} vs {crypto2_label} Price Comparison', fontsize=16, fontweight='bold')
    plt.xlabel('Year', fontsize=12)
    plt.ylabel('Price (USD)', fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.show()
# Example usage:
#plot_crypto_prices(btc_data, eth_data, crypto1_label='Bitcoin', crypto2_label='Ethereum')

# the deffirence betxeen the two coins is very high, so we can use log scale to better visualize the price movements of both coins on the same graph
def plot_crypto_prices_log_scale(crypto1_data, crypto2_data, crypto1_label='Crypto 1', crypto2_label='Crypto 2', plot = False):
    plt.figure(figsize=(14, 7))
    plt.plot(crypto1_data.index, crypto1_data['Close'], linewidth=2, label=crypto1_label)
    plt.plot(crypto2_data.index, crypto2_data['Close'], linewidth=2, label=crypto2_label)

    plt.title(f'{crypto1_label} vs {crypto2_label} Price Comparison (Log Scale)', fontsize=16, fontweight='bold')
    plt.xlabel('Year', fontsize=12)
    plt.ylabel('Price (USD)', fontsize=12)
    plt.yscale('log')
    plt.grid(True, alpha=0.3, which='both')
    plt.legend()
    plt.tight_layout()
    if plot:
        plt.show()
# Example usage:
# plot_crypto_prices_log_scale(btc_data, eth_data, crypto1_label='Bitcoin', crypto2_label='Ethereum', plot=True)


# use plot_crypto_prices_log_scale with all possible combinations of the two coins (btc and others coin or indexs) and save the plots as images
# Define a list of other cryptocurrencies to compare with Bitcoin
other_cryptos = ['ADA-USD', 'XRP-USD', 'SOL-USD', 'DOGE-USD', 'LTC-USD', 'BCH-USD', 'LINK-USD', 'DOT-USD', 'UNI-USD', 'AVAX-USD', 'MATIC-USD', 'ATOM-USD', 'ALGO-USD', 'VET-USD', 'FIL-USD', 'TRX-USD', 'XLM-USD', 'THETA-USD', 'AAVE-USD', 'EOS-USD', 'MKR-USD', 'COMP-USD', 'SUSHI-USD', 'YFI-USD', 'CRV-USD', 'SNX-USD', 'ZRX-USD', 'REN-USD', 'BAL-USD', 'GRT-USD', '1INCH-USD', 'KNC-USD', 'LRC-USD', 'OCEAN-USD', 'UMA-USD', 'BAND-USD', 'SRM-USD', 'RUNE-USD', 'CRO-USD', 'FTT-USD', 'GNO-USD', 'HNT-USD', 'KAVA-USD', 'LUNA-USD', 'NEAR-USD', 'RAY-USD', 'SAND-USD', 'STX-USD', 'WAVES-USD', 'ZIL-USD']

# Generate plots for each combination
def generate_plots_for_combinations(btc_data, other_cryptos):
    if not os.path.exists('plotsCOIN'):
        os.makedirs('plotsCOIN')
    for crypto in other_cryptos:
        try:
            crypto_data = yf.download(crypto, start='2015-01-01', end=datetime.now().strftime('%Y-%m-%d'))
            if crypto_data.empty:
                print(f"Skipping {crypto}: no data available")
                continue
            plot_crypto_prices_log_scale(btc_data, crypto_data, crypto1_label='Bitcoin', crypto2_label=crypto.split('-')[0])
            plt.savefig(f'plotsCOIN/bitcoin_vs_{crypto.split("-")[0]}.png')
            plt.close()  # Close the plot to free up memory
        except Exception as e:
            print(f"Error processing {crypto}: {e}")
            continue
# Example usage:
# generate_plots_for_combinations(btc_data, other_cryptos)

# Major Global Stock Indices
stock_indices = ['^GSPC', '^DJI', '^IXIC', '^FTSE', '^N225', '^HSI', '^BSESN', '^MXX', '^AXJO']
# Generate plots for Bitcoin vs Stock Indices
def generate_plots_for_stock_indices(btc_data, stock_indices):
    if not os.path.exists('plotsMGSI'):
        os.makedirs('plotsMGSI')
    for index in stock_indices:
        try:
            index_data = yf.download(index, start='2010-01-01', end=datetime.now().strftime('%Y-%m-%d'))
            if index_data.empty:
                print(f"Skipping {index}: no data available")
                continue
            plot_crypto_prices_log_scale(btc_data, index_data, crypto1_label='Bitcoin', crypto2_label=index.split('^')[1])
            plt.savefig(f'plotsMGSI/bitcoin_vs_{index.split("^")[1]}.png')
            plt.close()  # Close the plot to free up memory
        except Exception as e:
            print(f"Error processing {index}: {e}")
            continue

# Example usage:
# generate_plots_for_stock_indices(btc_data, stock_indices)

# Broad Market & Large Cap ETFs
etfs = ['SPY', 'QQQ', 'DIA', 'IWM', 'VTI', 'VOO', 'IVV', 'VEA', 'VWO', 'EFA']
# Generate plots for Bitcoin vs ETFs
def generate_plots_for_etfs(btc_data, etfs):
    if not os.path.exists('plotsETFs'):
        os.makedirs('plotsETFs')
    for etf in etfs:
        etf_data = yf.download(etf, start='2010-01-01', end=datetime.now().strftime('%Y-%m-%d'))
        plot_crypto_prices_log_scale(btc_data, etf_data, crypto1_label='Bitcoin', crypto2_label=etf)
        plt.savefig(f'plotsETFs/bitcoin_vs_{etf}.png')
        plt.close()  # Close the plot to free up memory 
        
# Example usage:
# generate_plots_for_etfs(btc_data, etfs)

# US Sector ETFs (The "Select Sector SPDRs")    
sector_etfs = ['XLY', 'XLP', 'XLE', 'XLF', 'XLV', 'XLI', 'XLB', 'XLRE', 'XLK', 'XLU']
# Generate plots for Bitcoin vs Sector ETFs
def generate_plots_for_sector_etfs(btc_data, sector_etfs):
    if not os.path.exists('plotsSectorETFs'):
        os.makedirs('plotsSectorETFs')
    for etf in sector_etfs:
        etf_data = yf.download(etf, start='2010-01-01', end=datetime.now().strftime('%Y-%m-%d'))
        plot_crypto_prices_log_scale(btc_data, etf_data, crypto1_label='Bitcoin', crypto2_label=etf)
        plt.savefig(f'plotsSectorETFs/bitcoin_vs_{etf}.png')
        plt.close()  # Close the plot to free up memory 
        
# Example usage:
# generate_plots_for_sector_etfs(btc_data, sector_etfs)

# Thematic, Factor & Growth ETFs
thematic_etfs = ['ARKK', 'ARKG', 'ARKW', 'ARKF', 'ARKQ', 'TAN', 'LIT', 'ICLN', 'PBW', 'CLOU']
# Generate plots for Bitcoin vs Thematic ETFs
def generate_plots_for_thematic_etfs(btc_data, thematic_etfs):
    if not os.path.exists('plotsThematicETFs'):
        os.makedirs('plotsThematicETFs')
    for etf in thematic_etfs:
        etf_data = yf.download(etf, start='2010-01-01', end=datetime.now().strftime('%Y-%m-%d'))
        plot_crypto_prices_log_scale(btc_data, etf_data, crypto1_label='Bitcoin', crypto2_label=etf)
        plt.savefig(f'plotsThematicETFs/bitcoin_vs_{etf}.png')
        plt.close()  # Close the plot to free up memory
        
# Example usage:
# generate_plots_for_thematic_etfs(btc_data, thematic_etfs)

# International & Emerging Markets
international_etfs = ['EEM', 'VWO', 'EWZ', 'EFA', 'VEA', 'IEMG', 'SCZ', 'GXC', 'FXI', 'MCHI']

# Generate plots for Bitcoin vs International ETFs
def generate_plots_for_international_etfs(btc_data, international_etfs):
    if not os.path.exists('plotsInternationalETFs'):
        os.makedirs('plotsInternationalETFs')
    for etf in international_etfs:
        etf_data = yf.download(etf, start='2010-01-01', end=datetime.now().strftime('%Y-%m-%d'))
        plot_crypto_prices_log_scale(btc_data, etf_data, crypto1_label='Bitcoin', crypto2_label=etf)
        plt.savefig(f'plotsInternationalETFs/bitcoin_vs_{etf}.png')
        plt.close()  # Close the plot to free up memory
        
# Example usage:
# generate_plots_for_international_etfs(btc_data, international_etfs)

# Bonds, Commodities & Crypto
bonds_commodities = ['TLT', 'GLD', 'SLV', 'USO', 'DBC', 'GSG', 'PDBC', 'BND', 'AGG', 'LQD']
# Generate plots for Bitcoin vs Bonds & Commodities ETFs
def generate_plots_for_bonds_commodities(btc_data, bonds_commodities):
    if not os.path.exists('plotsBondsCommodities'):
        os.makedirs('plotsBondsCommodities')
    for etf in bonds_commodities:
        etf_data = yf.download(etf, start='2010-01-01', end=datetime.now().strftime('%Y-%m-%d'))
        plot_crypto_prices_log_scale(btc_data, etf_data, crypto1_label='Bitcoin', crypto2_label=etf)
        plt.savefig(f'plotsBondsCommodities/bitcoin_vs_{etf}.png')
        plt.close()  # Close the plot to free up memory
        
# Example usage:
# generate_plots_for_bonds_commodities(btc_data, bonds_commodities)

# Generate all plots
def generate_all_plots(btc_data, other_cryptos, stock_indices, etfs, sector_etfs, thematic_etfs, international_etfs, bonds_commodities):
    generate_plots_for_combinations(btc_data, other_cryptos)
    generate_plots_for_stock_indices(btc_data, stock_indices)
    generate_plots_for_etfs(btc_data, etfs)
    generate_plots_for_sector_etfs(btc_data, sector_etfs)
    generate_plots_for_thematic_etfs(btc_data, thematic_etfs)
    generate_plots_for_international_etfs(btc_data, international_etfs)
    generate_plots_for_bonds_commodities(btc_data, bonds_commodities)
    
# Example usage:
generate_all_plots(btc_data, other_cryptos, stock_indices, etfs , sector_etfs, thematic_etfs, international_etfs, bonds_commodities)