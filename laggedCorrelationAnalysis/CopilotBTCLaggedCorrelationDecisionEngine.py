import re
import sys
from pathlib import Path
from typing import Dict, Any

import numpy as np
import pandas as pd


PERIOD_ORDER = {"1mo": 1, "3mo": 2, "6mo": 3, "1y": 4, "2y": 5, "3y": 6}


def parse_data(text: str) -> pd.DataFrame:
    """Parse analysis text into a DataFrame with columns:
    period, shift_days, rank, asset, correlation
    """
    rows = []
    lines = text.splitlines()
    i = 0
    header_re = re.compile(r"--- Analysis for Period: (?P<period>\S+) with Shift of (?P<shift>\d+) day\(s\) ---")
    asset_line_re = re.compile(r"^(?P<asset>\S[\S\- ]*?)\s{2,}(?P<corr>0?\.\d+|1\.0+)$")

    while i < len(lines):
        m = header_re.match(lines[i].strip())
        if m:
            period = m.group("period")
            shift = int(m.group("shift"))
            i += 1
            rank = 1
            # read up to next blank or a 'period' line
            while i < len(lines):
                line = lines[i].rstrip()
                if not line:
                    i += 1
                    continue
                if line.startswith("period") or line.startswith("--- Analysis"):
                    break

                # Format 1: table rows with an index, ticker, correlation, period, shift
                m_table = re.match(r"^\s*\d+\s+([^\s]+)\s+([0-9]*\.[0-9]+)\s+(\S+)\s+(\d+)\s*$", line)
                if m_table:
                    asset = m_table.group(1).strip()
                    try:
                        corr = float(m_table.group(2))
                    except ValueError:
                        i += 1
                        continue
                    rows.append({
                        "period": period,
                        "shift_days": shift,
                        "rank": rank,
                        "asset": asset,
                        "correlation": corr,
                    })
                    rank += 1
                    i += 1
                    continue

                # Format 2: simple 'ASSET    0.12345' style
                am = re.match(r"^([A-Za-z0-9\-_/\.]+)\s+([0-9]*\.?[0-9]+)$", line)
                if am:
                    asset = am.group(1).strip()
                    try:
                        corr = float(am.group(2))
                    except ValueError:
                        i += 1
                        continue
                    rows.append({
                        "period": period,
                        "shift_days": shift,
                        "rank": rank,
                        "asset": asset,
                        "correlation": corr,
                    })
                    rank += 1
                i += 1
            continue
        i += 1

    df = pd.DataFrame(rows)
    if not df.empty:
        df["shift_days"] = df["shift_days"].astype(int)
        df["correlation"] = df["correlation"].astype(float)
        df["period_order"] = df["period"].map(PERIOD_ORDER).fillna(0).astype(int)
    return df


def compute_metrics(df: pd.DataFrame) -> Dict[str, Any]:
    if df.empty:
        return {}

    metrics: Dict[str, Any] = {}

    # per-period aggregated stats
    per_period = df.groupby("period").agg(
        avg_corr=("correlation", "mean"),
        max_corr=("correlation", "max"),
        median_corr=("correlation", "median"),
    ).reset_index()
    metrics["per_period"] = per_period

    # short/mid/long buckets
    short = ["1mo", "3mo"]
    mid = ["6mo", "1y"]
    long = ["2y", "3y"]

    def bucket_avg(periods):
        sub = per_period[per_period["period"].isin(periods)]
        return float(sub["avg_corr"].mean()) if not sub.empty else float("nan")

    metrics["short_avg"] = bucket_avg(short)
    metrics["mid_avg"] = bucket_avg(mid)
    metrics["long_avg"] = bucket_avg(long)

    # correlation decay: slope of avg_corr vs period_order
    per_period_ordered = per_period.copy()
    per_period_ordered["order"] = per_period_ordered["period"].map(PERIOD_ORDER)
    per_period_ordered = per_period_ordered.dropna(subset=["order"])
    if len(per_period_ordered) >= 2:
        x = per_period_ordered["order"].values
        y = per_period_ordered["avg_corr"].values
        slope = np.polyfit(x, y, 1)[0]
    else:
        slope = 0.0
    metrics["decay_slope"] = float(slope)

    # trend of correlation vs shift_days (positive slope = larger shift -> larger corr)
    shift_trend = df.groupby("shift_days").agg(avg_corr=("correlation", "mean")).reset_index()
    if len(shift_trend) >= 2:
        st_x = shift_trend["shift_days"].values
        st_y = shift_trend["avg_corr"].values
        shift_slope = float(np.polyfit(st_x, st_y, 1)[0])
    else:
        shift_slope = 0.0
    metrics["shift_slope"] = shift_slope

    # top assets overall (counts and presence of risk-on keywords)
    top_assets = df.sort_values(["period_order", "rank"]).groupby(["period", "rank"]).first()
    all_top = df[df["rank"] <= 3]["asset"].value_counts()
    metrics["top_assets_counts"] = all_top.to_dict()

    risk_keywords = ["ARK", "ETF", "IGV", "TECH", "COIN", "-USD", "RAY", "ARKW"]
    risk_on_count = sum(any(k.upper() in a.upper() for k in risk_keywords) for a in df[df["rank"] <= 3]["asset"].unique())
    metrics["risk_on_count"] = int(risk_on_count)

    metrics["overall_avg"] = float(df["correlation"].mean())
    metrics["overall_median"] = float(df["correlation"].median())

    return metrics


def generate_signal(metrics: Dict[str, Any], scoring_params: Dict[str, float] = None) -> Dict[str, Any]:
    if not metrics:
        return {"signal": "SELL", "score": -10.0, "confidence": 0, "reason": "No data"}

    # scoring defaults
    params = {
        "short_weight": 3.0,
        "mid_weight": 1.5,
        "long_weight": -1.0,
        "shift_trend_weight": 1.0,
        "risk_on_weight": 0.5,
        "decay_penalty": -2.0,
    }
    if scoring_params:
        params.update(scoring_params)

    score = 0.0

    short_avg = metrics.get("short_avg", 0.0)
    mid_avg = metrics.get("mid_avg", 0.0)
    long_avg = metrics.get("long_avg", 0.0)
    shift_slope = metrics.get("shift_slope", 0.0)
    decay_slope = metrics.get("decay_slope", 0.0)
    risk_on_count = metrics.get("risk_on_count", 0)
    overall_avg = metrics.get("overall_avg", 0.0)

    # Positive signals
    if short_avg and short_avg > 0.7:
        score += params["short_weight"] * (short_avg - 0.7)
    if mid_avg and mid_avg > 0.6:
        score += params["mid_weight"] * (mid_avg - 0.6)
    if shift_slope and shift_slope > 0:
        score += params["shift_trend_weight"] * shift_slope
    score += params["risk_on_weight"] * risk_on_count

    # Negative signals
    if short_avg and short_avg < 0.3:
        score -= 2.0
    if long_avg and long_avg > 0.6 and short_avg < 0.4:
        score -= 1.5
    if overall_avg < 0.4:
        score -= 2.0
    # decay penalty (if slope negative -> decay)
    if decay_slope < 0:
        score += params["decay_penalty"] * abs(decay_slope)

    # decide
    signal = "BUY" if score > 0 else "SELL"

    # confidence: map score to 0-100 via logistic scaling
    conf = 1 / (1 + np.exp(-score / 2.0))
    confidence = int(round(conf * 100))

    # Construct reason
    reason_parts = []
    reason_parts.append(f"Short-term avg={short_avg:.3f}")
    reason_parts.append(f"Mid-term avg={mid_avg:.3f}")
    reason_parts.append(f"Long-term avg={long_avg:.3f}")
    reason_parts.append(f"Shift slope={shift_slope:.4f}")
    reason_parts.append(f"Decay slope={decay_slope:.4f}")
    if risk_on_count:
        reason_parts.append(f"Risk-on assets={risk_on_count}")

    reason = ", ".join(reason_parts)

    return {"signal": signal, "score": float(score), "confidence": confidence, "reason": reason}


def main(argv=None):
    argv = argv or sys.argv[1:]
    if not argv:
        print("Usage: python btc_decision_engine.py <analysis_text_file>")
        return 2
    path = Path(argv[0])
    if not path.exists():
        print(f"File not found: {path}")
        return 2

    text = path.read_text(encoding="utf-8")
    df = parse_data(text)
    metrics = compute_metrics(df)
    result = generate_signal(metrics)

    # Print summary
    print("--- BTC Lagged Correlation Decision Engine ---")
    if df.empty:
        print("No parsed data found in file.")
    else:
        print(f"Rows parsed: {len(df)}")
        print(f"Short-term avg: {metrics.get('short_avg'):.3f}")
        print(f"Mid-term avg: {metrics.get('mid_avg'):.3f}")
        print(f"Long-term avg: {metrics.get('long_avg'):.3f}")
        print(f"Decay slope: {metrics.get('decay_slope'):.4f}")
        print()
        print(f"Signal Score: {result['score']:+.3f}")
        print(f"Final Signal: {result['signal']} BTC")
        print(f"Confidence: {result['confidence']}%")
        print(f"Reason: {result['reason']}")

    # return BUY or SELL signal and info dict for potential further use
    return result['signal'], result


if __name__ == "__main__":
    raise SystemExit(main())
