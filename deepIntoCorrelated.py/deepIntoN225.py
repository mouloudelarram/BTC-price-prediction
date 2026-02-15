import yfinance as yf
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

# Download data for the last 10 years
end_date = datetime.now()
start_date = end_date - timedelta(days=365*10)

# Fetch BTC and N225 data
btc = yf.download('BTC-USD', start=start_date, end=end_date)
n225 = yf.download('^N225', start=start_date, end=end_date)

# Normalize both series to start at 100 for comparison
btc_normalized = (btc['Close'] / btc['Close'].iloc[0]) * 100
n225_normalized = (n225['Close'] / n225['Close'].iloc[0]) * 100

# Create single plot with both normalized series
plt.figure(figsize=(12, 6))
plt.semilogy(btc_normalized.index, btc_normalized, color='orange', linewidth=1.5, label='BTC-USD')
plt.semilogy(n225_normalized.index, n225_normalized, color='blue', linewidth=1.5, label='^N225')
plt.title('Bitcoin vs Nikkei 225 - Last 10 Years (Normalized)', fontsize=12, fontweight='bold')
plt.ylabel('Relative Price (Base = 100)', fontsize=10)
plt.xlabel('Date', fontsize=10)
plt.legend(fontsize=10)
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()
