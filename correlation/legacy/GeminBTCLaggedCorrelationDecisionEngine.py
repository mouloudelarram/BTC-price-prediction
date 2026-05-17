from ast import arg
import sys
import pandas as pd
import re

class BTCCorrelationAnalyzer:
    def __init__(self, raw_text):
        self.raw_text = raw_text
        self.data = None
        self.metrics = {}
        
    def parse_data(self):
        """Extracts period, shift, assets, and correlations from text."""
        # Split text by the separator header
        blocks = re.split(r'--- Analysis for Period:', self.raw_text)
        parsed_records = []

        for block in blocks[1:]: # Skip the first empty split
            try:
                # Extract Period and Shift
                header_match = re.search(r'(\w+)\s+with Shift of (\d+)', block)
                period = header_match.group(1)
                shift = int(header_match.group(2))

                # Extract Assets and Values (looks for Asset_Name Space Number)
                # Matches patterns like 'ARKW          0.888931'
                matches = re.findall(r'([A-Z0-9\.-]+)\s+([0-9\.]+)', block)
                
                for asset, corr in matches:
                    if asset not in ['period', 'shift_days']:
                        parsed_records.append({
                            'period': period,
                            'shift_days': shift,
                            'asset': asset,
                            'correlation': float(corr)
                        })
            except Exception as e:
                continue

        self.data = pd.DataFrame(parsed_records)
        return self.data

    def compute_metrics(self):
        """Categorizes periods and calculates strength across timeframes."""
        df = self.data
        
        # Categorization logic
        short_term = ['1mo', '3mo']
        mid_term = ['6mo', '1y']
        long_term = ['2y', '3y']

        self.metrics['short_avg'] = df[df['period'].isin(short_term)]['correlation'].mean()
        self.metrics['mid_avg'] = df[df['period'].isin(mid_term)]['correlation'].mean()
        self.metrics['long_avg'] = df[df['period'].isin(long_term)]['correlation'].mean()
        self.metrics['max_corr'] = df['correlation'].max()
        
        # Check for correlation "decay" (Is short-term > long-term?)
        self.metrics['is_decaying'] = self.metrics['short_avg'] < self.metrics['long_avg']
        
        # Check for Risk-On assets in top correlations (Tech/Growth)
        risk_on_identifiers = ['ARK', 'IGV', 'USD', 'ETH', 'BTC', 'QQQ', 'NVDA']
        top_assets = df.nlargest(10, 'correlation')['asset'].tolist()
        self.metrics['risk_on_count'] = sum(1 for a in top_assets if any(r in a for r in risk_on_identifiers))

    def generate_signal(self):
        """Rule-based scoring system for BUY/SELL."""
        score = 0.0
        reasons = []

        # 1. Short-term Strength
        if self.metrics['short_avg'] > 0.7:
            score += 2.5
            reasons.append("Strong short-term correlation (>0.7)")
        elif self.metrics['short_avg'] < 0.3:
            score -= 2.0
            reasons.append("Weak short-term predictive structure")

        # 2. Mid-term validation
        if self.metrics['mid_avg'] > 0.6:
            score += 1.5
            reasons.append("Mid-term correlation confirms trend")

        # 3. Structural Decay Check
        if self.metrics['is_decaying']:
            score -= 1.5
            reasons.append("Correlation decay: Long-term structure stronger than short-term")
        else:
            score += 1.0
            reasons.append("Positive structure: Short-term leads long-term")

        # 4. Asset Composition
        if self.metrics['risk_on_count'] >= 5:
            score += 1.0
            reasons.append("High concentration of risk-on assets in top correlations")

        # Final Determination
        signal = "BUY BTC" if score > 1.5 else "SELL BTC"
        confidence = min(abs(score) / 5.0 * 100, 100) # Simple normalization

        return {
            "Signal": signal,
            "Score": round(score, 2),
            "Confidence": f"{round(confidence, 1)}%",
            "Reasoning": reasons,
            "Metrics": self.metrics
        }

def main(input_text):
    analyzer = BTCCorrelationAnalyzer(input_text)
    analyzer.parse_data()
    analyzer.compute_metrics()
    result = analyzer.generate_signal()

    print("--- BTC TRADING SIGNAL REPORT ---")
    print(f"Final Signal: {result['Signal']}")
    print(f"Signal Score: {result['Score']}")
    print(f"Confidence:   {result['Confidence']}")
    print("\nLogic Breakdown:")
    for r in result['Reasoning']:
        print(f"- {r}")
    print("---------------------------------")
    
    # return BUY or SELL signal and detailed info for potential further use
    return result['Signal'], result

if __name__ == "__main__":
    # Example usage with the data snippet you provided
    sample_data = open(sys.argv[1], "r").read()

    main(sample_data)