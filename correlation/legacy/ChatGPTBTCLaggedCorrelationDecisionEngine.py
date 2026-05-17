import re
import pandas as pd
import numpy as np


# =========================
# 1️⃣ DATA PARSING
# =========================

def parse_data(file_path: str) -> pd.DataFrame:
    """
    Parse the raw text output of btc_lagged_correlation_analysis
    into a structured pandas DataFrame.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()

    header_re = re.compile(r'--- Analysis for Period:\s*(?P<period>\S+)\s*with Shift of\s*(?P<shift>\d+) day\(s\)\s*---')
    df_row_re = re.compile(r'^\s*\d+\s+([\^A-Za-z0-9\-]+)\s+(-?\d+\.\d+)\s+(\S+)\s+(\d+)\s*$')
    compact_row_re = re.compile(r'^\s*([\^A-Za-z0-9\-]+)\s+(-?\d+\.\d+)')

    lines = text.splitlines()
    records = []
    i = 0
    while i < len(lines):
        line = lines[i]
        m = header_re.search(line)
        if m:
            period = m.group('period')
            shift = int(m.group('shift'))
            # scan following lines for up to 3 asset rows
            found = 0
            j = i + 1
            while j < len(lines) and found < 3:
                l = lines[j].strip()
                if not l:
                    j += 1
                    continue

                mdf = df_row_re.match(l)
                if mdf:
                    asset = mdf.group(1)
                    corr = float(mdf.group(2))
                    records.append({
                        'period': period,
                        'shift_days': shift,
                        'asset': asset,
                        'correlation': corr,
                    })
                    found += 1
                    j += 1
                    continue

                mcomp = compact_row_re.match(l)
                if mcomp:
                    asset = mcomp.group(1)
                    corr = float(mcomp.group(2))
                    records.append({
                        'period': period,
                        'shift_days': shift,
                        'asset': asset,
                        'correlation': corr,
                    })
                    found += 1
                    j += 1
                    continue

                j += 1

            i = j
        else:
            i += 1

    if not records:
        return pd.DataFrame()

    df = pd.DataFrame(records)
    return df


# =========================
# 2️⃣ METRICS COMPUTATION
# =========================

def compute_metrics(df: pd.DataFrame) -> dict:
    """
    Compute short/mid/long-term correlation metrics.
    """

    short_term = ["1mo", "3mo"]
    mid_term = ["6mo", "1y"]
    long_term = ["2y", "3y"]

    metrics = {}

    def avg_corr(periods):
        return df[df["period"].isin(periods)]["correlation"].mean()

    metrics["short_avg"] = avg_corr(short_term)
    metrics["mid_avg"] = avg_corr(mid_term)
    metrics["long_avg"] = avg_corr(long_term)

    metrics["overall_max"] = df["correlation"].max()

    # Correlation strength trend by shift_days (recent predictive strength)
    shift_strength = (
        df.groupby("shift_days")["correlation"]
        .mean()
        .sort_index()
    )

    metrics["shift_trend"] = shift_strength.diff().mean()

    return metrics


# =========================
# 3️⃣ SIGNAL GENERATION
# =========================

def generate_signal(metrics: dict) -> tuple:
    """
    Generate BUY or SELL signal based on scoring model.
    """

    score = 0
    explanation = []

    # --- Short-term strength ---
    if metrics["short_avg"] > 0.7:
        score += 2
        explanation.append("Strong short-term correlations")
    elif metrics["short_avg"] > 0.5:
        score += 1
        explanation.append("Moderate short-term correlations")
    else:
        score -= 1
        explanation.append("Weak short-term correlations")

    # --- Mid-term strength ---
    if metrics["mid_avg"] > 0.6:
        score += 1
        explanation.append("Strong mid-term correlations")

    # --- Long-term decay ---
    if metrics["long_avg"] < 0.3:
        score += 1
        explanation.append("Weak long-term correlation (cyclical regime)")
    else:
        score -= 1
        explanation.append("Strong long-term correlation")

    # --- Strong predictive spikes ---
    if metrics["overall_max"] > 0.85:
        score += 2
        explanation.append("Very strong predictive correlation detected")

    # --- Shift trend ---
    if metrics["shift_trend"] > 0:
        score += 1
        explanation.append("Increasing predictive strength across shift days")
    else:
        score -= 1
        explanation.append("Decreasing predictive strength across shift days")

    # Final Decision
    if score > 2:
        signal = "BUY BTC"
    else:
        signal = "SELL BTC"

    # Confidence (scaled)
    confidence = min(100, max(0, 50 + score * 10))

    return signal, score, confidence, explanation


# =========================
# 4️⃣ MAIN EXECUTION
# =========================

def main(file_path: str):
    df = parse_data(file_path)

    if df.empty:
        print("No valid data found.")
        return

    metrics = compute_metrics(df)

    signal, score, confidence, explanation = generate_signal(metrics)

    print("\n====== BTC CORRELATION ANALYSIS SUMMARY ======")
    print(f"Short-Term Avg Correlation: {metrics['short_avg']:.4f}")
    print(f"Mid-Term Avg Correlation:   {metrics['mid_avg']:.4f}")
    print(f"Long-Term Avg Correlation:  {metrics['long_avg']:.4f}")
    print(f"Max Correlation Observed:   {metrics['overall_max']:.4f}")
    print(f"Shift Trend Strength:       {metrics['shift_trend']:.4f}")
    print("=============================================")

    print(f"\nSignal Score: {score}")
    print(f"Final Signal: {signal}")
    print(f"Confidence: {confidence}%")

    print("\nReasoning:")
    for reason in explanation:
        print(f"- {reason}")
        
    # return BUY or SELL signal and detailed info for potential further use
    return signal, {
        "score": score,
        "confidence": confidence,
        "explanation": explanation,
        "metrics": metrics
    }


# =========================
# RUN SCRIPT
# =========================

if __name__ == "__main__":
    import sys
    import os

    # Prefer CLI arg, then known output file, then legacy default
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        fallback = os.path.join("OutputLaggedCorrelationAnalysis", "lagged_correlation_output_summary.txt")
        if os.path.exists(fallback):
            file_path = fallback
        else:
            file_path = "btc_analysis_output.txt"

    print(f"Using input file: {file_path}")
    main(file_path)
