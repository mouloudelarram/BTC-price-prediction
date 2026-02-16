import pandas as pd
import yfinance as yf
import re
import json
from datetime import datetime

class BTCAutoTraderV3:
    def __init__(self, file_path):
        self.file_path = file_path
        self.weights = {"1mo": 1, "3mo": 2, "6mo": 3, "1y": 5, "2y": 3, "3y": 2}
        self.thresholds = {"short_term": 0.30, "long_term": 0.20}
        self.decision_threshold = 2.0  # Lowered slightly for sensitivity

    def parse_correlation_file(self):
        """Extracts data from the daily text summary."""
        data = []
        current_period = None
        current_shift = None
        try:
            with open(self.file_path, 'r') as f:
                for line in f:
                    header_match = re.search(r"Period: (\w+) with Shift of (\d+)", line)
                    if header_match:
                        current_period, current_shift = header_match.groups()
                        current_shift = int(current_shift)
                        continue
                    if re.match(r"^\s*\d+\s+", line) and "Ticker" not in line:
                        parts = line.split()
                        data.append({
                            "ticker": parts[1],
                            "correlation": float(parts[2]),
                            "period": current_period,
                            "shift_days": current_shift
                        })
            return pd.DataFrame(data)
        except Exception as e:
            print(f"File Error: {e}")
            return pd.DataFrame()

    def get_market_direction(self, ticker, shift_days):
        """Fetches history and determines if the lead asset is up or down."""
        try:
            # Using history(period='1mo') is more stable than specific start/end dates
            t = yf.Ticker(ticker)
            hist = t.history(period="1mo", interval="1d")
            
            if hist.empty or len(hist) < shift_days + 1:
                return 0 # Not enough data
            
            # Use 'Close' price. We compare today's last price vs the price X days ago
            price_now = hist['Close'].iloc[-1]
            price_then = hist['Close'].iloc[-(shift_days + 1)]
            
            if price_now > price_then: return 1
            if price_now < price_then: return -1
            return 0
        except Exception:
            return 0

    def run(self):
        df = self.parse_correlation_file()
        if df.empty: return {"error": "No data found"}

        # Filtering logic
        df = df[df.apply(lambda r: r['correlation'] >= (self.thresholds["short_term"] if r['period'] in ['1mo', '3mo'] else self.thresholds["long_term"]), axis=1)]
        
        print(f"Processing {len(df)} significant assets...")
        total_score = 0
        max_potential = 0
        contributors = []

        for _, row in df.iterrows():
            direction = self.get_market_direction(row['ticker'], row['shift_days'])
            
            # If the lead asset moved, calculate the impact
            weight = self.weights.get(row['period'], 1)
            impact_value = row['correlation'] * weight
            contribution = impact_value * direction
            
            total_score += contribution
            max_potential += impact_value
            
            if direction != 0:
                contributors.append({
                    "ticker": row['ticker'],
                    "impact": round(contribution, 3),
                    "period": row['period'],
                    "move": "UP" if direction > 0 else "DOWN"
                })

        # Final Signal
        signal = "HOLD"
        if total_score >= self.decision_threshold: signal = "BUY"
        elif total_score <= -self.decision_threshold: signal = "SELL"

        confidence = (abs(total_score) / max_potential * 100) if max_potential > 0 else 0
        
        return {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "signal": signal,
            "confidence": f"{round(confidence, 1)}%",
            "net_score": round(total_score, 2),
            "analyzed_count": len(contributors),
            "top_contributors": sorted(contributors, key=lambda x: abs(x['impact']), reverse=True)[:5]
        }

# Run Engine
if __name__ == "__main__":
    PATH = "OutputLaggedCorrelationAnalysis/Old/lagged_correlation_output_summary_20260216_202839.txt"
    engine = BTCAutoTraderV3(PATH)
    print(json.dumps(engine.run(), indent=4))