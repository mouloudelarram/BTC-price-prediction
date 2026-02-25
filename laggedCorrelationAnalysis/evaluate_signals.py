"""Evaluate previously-taken BUY/SELL decisions against BTC price movement.

Uses real-time BTC/USDT data from Binance public REST API (no API key required).

Usage:
  - Evaluate a single decision:
      python evaluate_signals.py --date 2026-02-14 --decision BUY

  - Evaluate a CSV of decisions (columns: date,decision[,label]):
      python evaluate_signals.py --file decisions.csv
      
  - Optional JSON output:
      python evaluate_signals.py --date 2026-02-14 --decision BUY --output result.json

The script compares the close price on the decision date with the next
available BTC close and reports whether the decision was correct
(BUY -> price up, SELL -> price down), percent return, and aggregate
statistics for multiple decisions.
"""
from __future__ import annotations

import argparse
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Optional

from matplotlib.pylab import rand
import pandas as pd
import requests

# ---------------------------------------------------------------------------
# Binance REST helpers
# ---------------------------------------------------------------------------

BINANCE_BASE = "https://api.binance.com"
SYMBOL = "BTCUSDT"
INTERVAL = "1d"


def _date_to_ms(date_str: str) -> int:
    """Convert 'YYYY-MM-DD' to UTC midnight milliseconds (Binance open time)."""
    dt = datetime.fromisoformat(date_str).replace(tzinfo=timezone.utc)
    return int(dt.timestamp() * 1000)


def fetch_klines(start_date: str, end_date: str) -> pd.DataFrame:
    """Fetch daily OHLCV klines for BTCUSDT from Binance between two dates (inclusive).

    Args:
        start_date: 'YYYY-MM-DD'
        end_date:   'YYYY-MM-DD'

    Returns:
        DataFrame with columns: open_time, open, high, low, close, volume, date
    """
    start_ms = _date_to_ms(start_date)
    # end_date +1 day so we include the end_date candle (Binance endTime is exclusive)
    end_dt = datetime.fromisoformat(end_date).replace(tzinfo=timezone.utc) + timedelta(days=2)
    end_ms = int(end_dt.timestamp() * 1000)

    url = f"{BINANCE_BASE}/api/v3/klines"
    params = {
        "symbol": SYMBOL,
        "interval": INTERVAL,
        "startTime": start_ms,
        "endTime": end_ms,
        "limit": 100,
    }

    resp = requests.get(url, params=params, timeout=10)
    resp.raise_for_status()
    raw = resp.json()

    if not raw:
        return pd.DataFrame()

    # Binance kline fields: [open_time, open, high, low, close, volume, ...]
    cols = ["open_time", "open", "high", "low", "close", "volume",
            "close_time", "quote_asset_volume", "num_trades",
            "taker_buy_base", "taker_buy_quote", "ignore"]
    df = pd.DataFrame(raw, columns=cols)
    df["open_time"] = pd.to_numeric(df["open_time"])
    df["close"] = pd.to_numeric(df["close"])
    df["open"] = pd.to_numeric(df["open"])
    df["date"] = pd.to_datetime(df["open_time"], unit="ms", utc=True).dt.date
    return df[["open_time", "date", "open", "high", "low", "close", "volume"]]


def get_current_price() -> float:
    """Fetch the latest BTC/USDT price from Binance ticker."""
    url = f"{BINANCE_BASE}/api/v3/ticker/price"
    resp = requests.get(url, params={"symbol": SYMBOL}, timeout=10)
    resp.raise_for_status()
    return float(resp.json()["price"])


# ---------------------------------------------------------------------------
# Core evaluation logic
# ---------------------------------------------------------------------------

def fetch_next_close(t: str) -> Dict:
    """Fetch BTC close for date t and the next available trading day from Binance.

    Args:
        t: date string 'YYYY-MM-DD'

    Returns:
        dict with keys: date, close, next_date, next_close
    """
    dt = datetime.fromisoformat(t).date()
    start = (dt - timedelta(days=0)).isoformat()
    end = (dt + timedelta(days=7)).isoformat()

    df = fetch_klines(start, end)
    if df.empty:
        raise RuntimeError(f"No price data for BTC around {t}")

    # find last available close on or before requested date
    prior = df[df["date"].apply(lambda x: x <= dt)]
    if prior.empty:
        raise RuntimeError(f"No BTC close on or before {t}")

    close_date = prior["date"].iat[-1]
    close_price = float(prior["close"].iat[-1])

    # find next available close after that date
    later = df[df["date"].apply(lambda x: x > close_date)]

    if later.empty:
        # If the decision date is today or very recent, use live ticker as "next close"
        today = datetime.now(timezone.utc).date()
        if close_date >= today - timedelta(days=1):
            live_price = get_current_price()
            return {
                "date": close_date.isoformat(),
                "close": close_price,
                "next_date": today.isoformat(),
                "next_close": live_price,
                "live": True,
            }
        return {
            "date": close_date.isoformat(),
            "close": close_price,
            "next_date": None,
            "next_close": None,
        }

    next_date = later["date"].iat[0]
    next_close = float(later["close"].iat[0])
    return {
        "date": close_date.isoformat(),
        "close": close_price,
        "next_date": next_date.isoformat(),
        "next_close": next_close,
        "live": False,
    }


def evaluate_single(decision_date: str, decision: str) -> Dict:
    decision = decision.upper()
    if decision not in ("BUY", "SELL"):
        return {"decision_date": decision_date, "decision": decision, "error": "decision must be BUY or SELL"}

    rec = fetch_next_close(decision_date)
    if rec["next_close"] is None:
        return {"decision_date": decision_date, "decision": decision, "error": "no next close available"}

    ret = (rec["next_close"] - rec["close"]) / rec["close"]
    correct = (decision == "BUY" and ret > 0) or (decision == "SELL" and ret < 0)

    result = {
        "decision_date": rec["date"],
        "decision": decision,
        "price_then": rec["close"],
        "price_next": rec["next_close"],
        "next_date": rec["next_date"],
        "return": float(ret),
        "correct": bool(correct),
    }
    if rec.get("live"):
        result["note"] = "next_close is live Binance ticker price"
    return result


def evaluate_batch(df: pd.DataFrame) -> pd.DataFrame:
    records = []
    for _, row in df.iterrows():
        date = str(row["date"])
        decision = str(row["decision"])
        try:
            out = evaluate_single(date, decision)
        except Exception as e:
            out = {"decision_date": date, "decision": decision, "error": str(e)}
        records.append(out)
        time.sleep(0.1)  # gentle rate-limiting for Binance API
    return pd.DataFrame(records)


def summarize_results(res_df: pd.DataFrame) -> Dict:
    """Compute aggregate statistics, excluding errored rows."""
    if "error" in res_df.columns:
        valid = res_df[res_df["error"].isna()].copy()
    else:
        valid = res_df.copy()

    if valid.empty or "correct" not in valid.columns:
        return {
            "total": len(res_df),
            "valid": 0,
            "errors": len(res_df),
            "correct": 0,
            "accuracy_pct": 0.0,
            "avg_return_pct": 0.0,
            "avg_return_correct_pct": 0.0,
            "avg_return_incorrect_pct": 0.0,
            "cumulative_pnl": 0.0,
        }

    ok = valid[valid["correct"] == True]
    nok = valid[valid["correct"] == False]
    total = len(valid)
    correct = len(ok)
    accuracy = float(correct) / total * 100 if total > 0 else 0.0
    avg_return = float(valid["return"].mean()) * 100 if "return" in valid.columns else 0.0
    avg_return_correct = float(ok["return"].mean()) * 100 if not ok.empty else 0.0
    avg_return_incorrect = float(nok["return"].mean()) * 100 if not nok.empty else 0.0
    pnl = float(valid["return"].sum())

    return {
        "total": len(res_df),
        "valid": total,
        "errors": len(res_df) - total,
        "correct": correct,
        "accuracy_pct": round(accuracy, 2),
        "avg_return_pct": round(avg_return, 4),
        "avg_return_correct_pct": round(avg_return_correct, 4),
        "avg_return_incorrect_pct": round(avg_return_incorrect, 4),
        "cumulative_pnl": round(pnl, 6),
    }


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main():
    p = argparse.ArgumentParser(
        description="Evaluate BTC BUY/SELL decisions using real-time Binance data."
    )
    p.add_argument("--file", "-f", help="CSV file with columns date,decision", type=str)
    p.add_argument("--date", "-d", help="Single decision date YYYY-MM-DD", type=str)
    p.add_argument("--decision", help="BUY or SELL (used with --date)", type=str)
    p.add_argument("--output", "-o", help="Optional JSON output file for results", type=str)
    args = p.parse_args()

    if args.file:
        df = pd.read_csv(args.file)
        if not {"date", "decision"}.issubset(df.columns):
            raise SystemExit("CSV must contain 'date' and 'decision' columns")
        res = evaluate_batch(df)
    elif args.date and args.decision:
        res = pd.DataFrame([evaluate_single(args.date, args.decision)])
    else:
        raise SystemExit("Provide --file or both --date and --decision")

    # Pretty-print results
    print("\n=== Evaluation Results ===")
    print(res.to_string(index=False))

    summary = summarize_results(res)
    print("\n=== Summary ===")
    for k, v in summary.items():
        print(f"  {k}: {v}")

    if args.output:
        Path(args.output).write_text(res.to_json(orient="records", indent=2), encoding="utf-8")
        print(f"\nResults saved to {args.output}")

    if args.file:
        return summary
    else:
        return res["correct"].iat[0] if "correct" in res.columns else None

# ---------------------------------------------------------------------------
# test random dicisions
# ---------------------------------------------------------------------------
# generate random decisions for the past n days and evaluate them to see how the model would have performed historically. 
# This can help identify any biases or patterns in the decision-making process and provide insights for further improvements.
def test_random_decisions(days: int = 30, default_decision: str = None):
    today = datetime.now().date() 
    yesterday = today - timedelta(days=1)
    
    records = []
    # today decison not included
    for i in range(days):
        date = (yesterday - timedelta(days=i)).isoformat()
        if not default_decision:
            decision = "BUY" if rand() > 0.5 else "SELL"
        else:
            decision = default_decision
       
        records.append({"date": date, "decision": decision})
    df = pd.DataFrame(records)
    # print(df)
    res = evaluate_batch(df)
    summary = summarize_results(res)
    print("\n=== Random Decisions Test Summary ===")
    for k, v in summary.items():
        print(f"  {k}: {v}")

if __name__ == "__main__":
    result = main()
    print(f"\nFinal result: {result}")