"""Evaluate previously-taken BUY/SELL decisions against BTC price movement.

Usage:
  - Evaluate a single decision:
      python evaluate_signals.py --date 2026-02-14 --decision BUY

  - Evaluate a CSV of decisions (columns: date,decision[,label]):
      python evaluate_signals.py --file decisions.csv

The script compares the close price on the decision date with the next
available BTC close (typically 'today') and reports whether the decision
was correct (BUY -> price up, SELL -> price down), percent return, and
aggregate statistics for multiple decisions.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List

import pandas as pd
import yfinance as yf


def fetch_next_close(t: str) -> Dict[str, float]:
    """Fetch BTC close for date t and the next available trading day.

    t: date string 'YYYY-MM-DD'
    Returns dict with 'date', 'close', 'next_date', 'next_close'.
    """
    dt = datetime.fromisoformat(t).date()
    start = dt - timedelta(days=1)
    end = dt + timedelta(days=7)
    df = yf.download("BTC-USD", start=start.isoformat(), end=end.isoformat(), progress=False)
    if df.empty:
        raise RuntimeError(f"No price data for BTC around {t}")

    # find close on or after dt
    df = df.reset_index()
    # Normalize to python date for safe scalar comparisons
    df["date"] = pd.to_datetime(df["Date"]).dt.date
    # find last available close on or before requested date
    prior = df[df["date"].apply(lambda x: x <= dt)]
    if prior.empty:
        raise RuntimeError(f"No BTC close on or before {t}")
    close_dt = prior.iloc[-1]
    close_date = pd.to_datetime(prior["date"].iat[-1]).date()
    # find next available close after that date
    later = df[df["date"].apply(lambda x: x > close_date)]
    if later.empty:
        # if there's no later price in range, return same day (no next day)
        return {
            "date": close_date.isoformat(),
            "close": float(close_dt["Close"].iloc[0]),  # FIX 1: Added .iloc[0]
            "next_date": None,
            "next_close": None,
        }
    next_row = later.iloc[0]
    next_date = pd.to_datetime(later["date"].iat[0]).date()
    return {
        "date": close_date.isoformat(),
        "close": float(close_dt["Close"].iloc[0]),  # FIX 1: Added .iloc[0]
        "next_date": next_date.isoformat(),
        "next_close": float(next_row["Close"].iloc[0]),  # FIX 1: Added .iloc[0]
    }


def evaluate_single(decision_date: str, decision: str) -> Dict:
    decision = decision.upper()
    rec = fetch_next_close(decision_date)
    if rec["next_close"] is None:
        return {"decision_date": decision_date, "decision": decision, "error": "no next close available"}

    ret = (rec["next_close"] - rec["close"]) / rec["close"]
    correct = (decision == "BUY" and ret > 0) or (decision == "SELL" and ret < 0)
    return {
        "decision_date": rec["date"],
        "decision": decision,
        "price_then": rec["close"],
        "price_next": rec["next_close"],
        "next_date": rec["next_date"],
        "return": float(ret),
        "correct": bool(correct),
    }


def evaluate_batch(df: pd.DataFrame) -> pd.DataFrame:
    records = []
    for _, row in df.iterrows():
        date = str(row["date"]) if "date" in row else str(row[0])
        decision = str(row["decision"]) if "decision" in row else str(row[1])
        try:
            out = evaluate_single(date, decision)
        except Exception as e:
            out = {"decision_date": date, "decision": decision, "error": str(e)}
        records.append(out)
    return pd.DataFrame(records)


def summarize_results(res_df: pd.DataFrame) -> Dict:
    # FIX 2: Filter out rows with errors before checking 'correct' column
    valid_results = res_df[~res_df.get("error", pd.Series([False]*len(res_df))).notna()]
    
    if valid_results.empty or "correct" not in valid_results.columns:
        return {
            "total": len(res_df),
            "correct": 0,
            "accuracy_pct": 0.0,
            "avg_return": 0.0,
            "avg_return_correct": 0.0,
            "avg_return_incorrect": 0.0,
            "cumulative_pnl": 0.0,
        }
    
    ok = valid_results[valid_results["correct"] == True]
    nok = valid_results[valid_results["correct"] == False]
    total = len(valid_results)
    correct = len(ok)
    accuracy = float(correct) / total * 100 if total > 0 else 0.0
    avg_return = float(valid_results["return"].mean()) if "return" in valid_results else 0.0
    avg_return_correct = float(ok["return"].mean()) if not ok.empty else 0.0
    avg_return_incorrect = float(nok["return"].mean()) if not nok.empty else 0.0
    pnl = valid_results["return"].sum()  # assume 1 unit per decision
    return {
        "total": total,
        "correct": correct,
        "accuracy_pct": accuracy,
        "avg_return": avg_return,
        "avg_return_correct": avg_return_correct,
        "avg_return_incorrect": avg_return_incorrect,
        "cumulative_pnl": float(pnl),
    }


def main():
    p = argparse.ArgumentParser(description="Evaluate BTC BUY/SELL decisions against next-day BTC price movement.")
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

    print(res.to_string(index=False))
    summary = summarize_results(res)
    print("\nSummary:")
    for k, v in summary.items():
        print(f"- {k}: {v}")

    if args.output:
        Path(args.output).write_text(res.to_json(orient="records"), encoding="utf-8")
        
    # return True or false for single decision, or summary dict for batch
    if args.file:
        return summary
    else:
        return res["correct"].iat[0] if "correct" in res else None   


if __name__ == "__main__":
    print(main())
 
 # how to run - for single decision: python evaluate_signals.py --date 2026-02-14 --decision BUY