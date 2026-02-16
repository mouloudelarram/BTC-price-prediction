import re
import pandas as pd
from typing import Tuple, Dict, Any


############################
# Parsing
############################

SECTION_HEADER_RE = re.compile(
    r"--- Analysis for Period:\s*(?P<period>\S+)\s*with Shift of\s*(?P<shift>\d+)\s*day\(s\)\s*---",
    re.IGNORECASE,
)

ASSET_LINE_RE = re.compile(r"^(?P<asset>[A-Z0-9\-]+)\s+(?P<corr>-?\d+\.\d+)\s*$")


def parse_data(text: str) -> pd.DataFrame:
    """
    Parse the btc_lagged_correlation_analysis() text output into a DataFrame.

    Columns:
    - period: str
    - shift_days: int
    - rank: int (1–3)
    - asset: str
    - corr: float
    """
    records = []

    # tolerant regexes for DataFrame-style and compact rows
    df_row_re = re.compile(r'^\s*\d+\s+(?P<asset>\S+)\s+(?P<corr>-?\d+\.\d+)')
    compact_re = re.compile(r'^\s*(?P<asset>\S+)\s+(?P<corr>-?\d+\.\d+)')

    lines = text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        m_header = SECTION_HEADER_RE.search(line)
        if m_header:
            period = m_header.group('period')
            shift = int(m_header.group('shift'))
            # scan next lines for up to 3 asset rows
            found = 0
            j = i + 1
            while j < len(lines) and found < 3:
                l = lines[j].strip()
                if not l:
                    j += 1
                    continue

                mdf = df_row_re.match(l)
                if mdf:
                    asset = mdf.group('asset')
                    corr = float(mdf.group('corr'))
                    records.append({'period': period, 'shift_days': shift, 'rank': found+1, 'asset': asset, 'corr': corr})
                    found += 1
                    j += 1
                    continue

                mcomp = compact_re.match(l)
                if mcomp:
                    asset = mcomp.group('asset')
                    corr = float(mcomp.group('corr'))
                    records.append({'period': period, 'shift_days': shift, 'rank': found+1, 'asset': asset, 'corr': corr})
                    found += 1
                    j += 1
                    continue

                j += 1

            i = j
        else:
            i += 1

    if not records:
        raise ValueError("No correlation sections parsed from input text.")

    df = pd.DataFrame(records)
    return df


############################
# Metrics / Feature Engineering
############################

SHORT_TERM = ["1mo", "3mo"]
MID_TERM = ["6mo", "1y"]
LONG_TERM = ["2y", "3y"]


def compute_period_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate metrics per period and shift, then per period.

    Returns DataFrame indexed by period with:
      - avg_corr
      - max_corr
      - std_corr
      - avg_corr_by_shift (dict)
      - max_shift_corr
      - min_shift_corr
    """
    if df.empty:
        raise ValueError("Empty DataFrame passed to compute_period_metrics().")

    # Aggregate by period and shift
    grouped_ps = (
        df.groupby(["period", "shift_days"])["corr"]
        .agg(["mean", "max"])
        .rename(columns={"mean": "avg_corr_shift", "max": "max_corr_shift"})
        .reset_index()
    )

    # Period-level aggregation
    period_stats = (
        grouped_ps.groupby("period")
        .agg(
            avg_corr=("avg_corr_shift", "mean"),
            max_corr=("max_corr_shift", "max"),
            std_corr=("avg_corr_shift", "std"),
        )
        .fillna(0.0)
    )

    # Correlation trend across shifts (store as dict for later use)
    avg_by_shift = (
        grouped_ps.groupby(["period", "shift_days"])["avg_corr_shift"]
        .mean()
        .reset_index()
    )

    shift_maps = {}
    for period in period_stats.index:
        sub = avg_by_shift[avg_by_shift["period"] == period]
        shift_maps[period] = dict(
            zip(sub["shift_days"].astype(int).tolist(), sub["avg_corr_shift"].tolist())
        )

    period_stats["avg_corr_by_shift"] = period_stats.index.map(shift_maps.get)

    # For decay/strength detection, keep min/max across shifts
    max_shift_corr = []
    min_shift_corr = []
    for period in period_stats.index:
        shifts = period_stats.loc[period, "avg_corr_by_shift"] or {}
        if len(shifts) > 0:
            vals = list(shifts.values())
            max_shift_corr.append(max(vals))
            min_shift_corr.append(min(vals))
        else:
            max_shift_corr.append(0.0)
            min_shift_corr.append(0.0)

    period_stats["max_shift_corr"] = max_shift_corr
    period_stats["min_shift_corr"] = min_shift_corr

    return period_stats


def compute_horizon_metrics(period_stats: pd.DataFrame) -> Dict[str, Dict[str, float]]:
    """
    Compute short-, mid-, and long-term aggregates.

    Returns dict:
      {
        "short": {"avg_corr": ..., "max_corr": ...},
        "mid":   {...},
        "long":  {...},
      }
    """
    def agg_for(period_list):
        sub = period_stats.loc[period_stats.index.intersection(period_list)]
        if sub.empty:
            return {"avg_corr": 0.0, "max_corr": 0.0}
        return {
            "avg_corr": float(sub["avg_corr"].mean()),
            "max_corr": float(sub["max_corr"].max()),
        }

    return {
        "short": agg_for(SHORT_TERM),
        "mid": agg_for(MID_TERM),
        "long": agg_for(LONG_TERM),
    }


def compute_trend_score(period_stats: pd.DataFrame) -> float:
    """
    Measure whether correlation tends to increase with larger shift_days.

    Approach:
      - For each period, compute correlation between shift_days and avg_corr_by_shift.
      - Average those correlations across periods.
    """
    import numpy as np

    trend_values = []
    for period, row in period_stats.iterrows():
        shift_map = row["avg_corr_by_shift"] or {}
        if len(shift_map) <= 1:
            continue
        xs = np.array(sorted(shift_map.keys()), dtype=float)
        ys = np.array([shift_map[k] for k in sorted(shift_map.keys())], dtype=float)
        if np.std(xs) == 0 or np.std(ys) == 0:
            continue
        corr = float(np.corrcoef(xs, ys)[0, 1])
        trend_values.append(corr)

    if not trend_values:
        return 0.0

    return float(np.mean(trend_values))


############################
# Signal Logic
############################

def generate_signal(
    df: pd.DataFrame,
    risk_on_assets: Tuple[str, ...] = ("ARKK", "ARKW", "QQQ", "NDX", "SOXL", "IGV", "RAY-USD"),
    buy_threshold: float = 0.0,
) -> Tuple[str, Dict[str, Any]]:
    """
    Generate BUY/SELL BTC signal based on lagged correlation structure.

    Returns:
      signal: "BUY BTC" or "SELL BTC"
      info:   dict with score, components, confidence, explanation, metrics
    """
    period_stats = compute_period_metrics(df)
    horizons = compute_horizon_metrics(period_stats)
    trend_score = compute_trend_score(period_stats)

    short_avg = horizons["short"]["avg_corr"]
    mid_avg = horizons["mid"]["avg_corr"]
    long_avg = horizons["long"]["avg_corr"]

    # BUY / SELL scoring rules
    score = 0.0
    components = {}

    # 1) Strong short-term correlations
    if short_avg > 0.7:
        s = 2.0
        score += s
        components["short_term_strong"] = s

    # Moderate short-term correlations
    elif short_avg > 0.5:
        s = 1.0
        score += s
        components["short_term_moderate"] = s

    else:
        s = -1.0
        score += s
        components["short_term_weak"] = s

    # 2) Strong mid-term correlations (6m, 1y)
    if mid_avg > 0.7:
        s = 2.0
        score += s
        components["mid_term_strong"] = s
    elif mid_avg > 0.5:
        s = 1.0
        score += s
        components["mid_term_moderate"] = s
    else:
        s = -0.5
        score += s
        components["mid_term_weak"] = s

    # 3) Long-term vs short-term: strong long-term but weak short-term is bearish
    if long_avg > 0.5 and short_avg < 0.3:
        s = -2.0
        score += s
        components["long_strong_short_weak"] = s

    # 4) Overall low correlations = bearish
    global_avg = float(df["corr"].mean())
    if global_avg < 0.4:
        s = -1.0
        score += s
        components["global_low_corr"] = s
    elif global_avg > 0.7:
        s = 1.0
        score += s
        components["global_high_corr"] = s

    # 5) Correlation trend across shifts (increasing shifts => bullish)
    if trend_score > 0.3:
        s = 1.5
        score += s
        components["increasing_shift_corr"] = s
    elif trend_score < -0.3:
        s = -1.5
        score += s
        components["decreasing_shift_corr"] = s

    # 6) Presence of risk-on assets among top correlations
    # Count unique risk-on assets in top lists where corr > 0.7
    risk_on_set = set(risk_on_assets)
    high_corr_risk_on = (
        df[(df["corr"] > 0.7) & (df["asset"].isin(risk_on_set))]["asset"].nunique()
    )
    if high_corr_risk_on >= 2:
        s = 2.0
        score += s
        components["risk_on_strong_presence"] = s
    elif high_corr_risk_on == 1:
        s = 1.0
        score += s
        components["risk_on_some_presence"] = s

    # 7) Correlation decay across horizons (short > mid > long)
    if short_avg > mid_avg > long_avg:
        s = 1.0
        score += s
        components["short_mid_long_decay"] = s
    elif long_avg > short_avg:
        s = -1.0
        score += s
        components["long_dominant"] = s

    # Decide final signal
    signal = "BUY BTC" if score > buy_threshold else "SELL BTC"

    # Confidence heuristic
    # Map absolute score into [0, 100] using simple saturating function
    abs_score = abs(score)
    max_reasonable = 8.0
    confidence = min(100.0, (abs_score / max_reasonable) * 100.0)

    # Explanation string
    reasons = []
    if short_avg > 0.7:
        reasons.append("strong short-term correlations (>0.7) across 1–3 month periods")
    if mid_avg > 0.6:
        reasons.append("solid mid-term correlations in 6m–1y horizon")
    if long_avg < 0.3:
        reasons.append("weak long-term structural correlation in 2y–3y")
    if trend_score > 0.3:
        reasons.append("increasing correlation with larger shift days")
    if high_corr_risk_on >= 1:
        reasons.append("high correlations with risk-on assets such as tech ETFs or crypto")

    if not reasons:
        reasons.append("mixed correlation structure without dominant bullish or bearish regime")

    explanation = (
        f"Signal driven by {', '.join(reasons)}. "
        f"Short-term avg corr={short_avg:.2f}, mid-term={mid_avg:.2f}, long-term={long_avg:.2f}, "
        f"trend_score={trend_score:.2f}."
    )

    info = {
        "score": score,
        "components": components,
        "confidence": confidence,
        "explanation": explanation,
        "metrics": {
            "short_term": horizons["short"],
            "mid_term": horizons["mid"],
            "long_term": horizons["long"],
            "trend_score": trend_score,
            "global_avg_corr": global_avg,
        },
    }

    return signal, info


############################
# Main CLI / Orchestrator
############################

def main(input_path: str) -> None:
    # Read file
    with open(input_path, "r", encoding="utf-8") as f:
        text = f.read()

    # Step 1: Parse
    df = parse_data(text)

    # Step 2: Metrics
    period_stats = compute_period_metrics(df)
    horizons = compute_horizon_metrics(period_stats)

    # Step 3: Signal
    signal, info = generate_signal(df)

    # Output summary
    print("=== BTC Lagged Correlation Summary ===")
    print("Per-period metrics:")
    print(
        period_stats[["avg_corr", "max_corr", "std_corr"]]
        .sort_index()
        .to_string(float_format=lambda x: f"{x:0.3f}")
    )
    print()

    print("Horizon metrics:")
    for horizon_name, vals in horizons.items():
        print(
            f"  {horizon_name.capitalize()} term: "
            f"avg_corr={vals['avg_corr']:.3f}, max_corr={vals['max_corr']:.3f}"
        )
    print()

    print(f"Signal Score: {info['score']:.2f}")
    print(f"Confidence: {info['confidence']:.1f}%")
    print(f"Final Signal: {signal}")
    print(f"Reason: {info['explanation']}")
    
    # return BUY or SELL signal and info dict for potential further use
    return signal, info


if __name__ == "__main__":
    # Example:
    # python btc_decision_engine.py btc_lagged_correlation_output.txt
    import sys

    if len(sys.argv) < 2:
        print("Usage: python btc_decision_engine.py <analysis_output.txt>")
        sys.exit(1)

    main(sys.argv[1])

# call python PerplexityBTCLaggedCorrelationDecisionEngine.py OutputLaggedCorrelationAnalysis/lagged_correlation_output_summary.txt