"""CLI script for backtesting trading decisions."""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import argparse
import json
import time
from typing import Dict, List
from datetime import datetime

import pandas as pd

from app.data.loaders import BinanceDataLoader
from app.models import BacktestResult, BacktestSummary
from app.utils.logger import get_logger

logger = get_logger(__name__)


class BacktestEngine:
    """Backtest trading decisions against actual price data."""

    def __init__(self):
        self.loader = BinanceDataLoader()

    def evaluate_single_decision(self, decision_date: str, decision: str) -> Dict:
        """
        Evaluate a single BUY/SELL decision.

        Args:
            decision_date: 'YYYY-MM-DD'
            decision: 'BUY' or 'SELL'

        Returns:
            Dict with evaluation result
        """
        decision = decision.upper()

        if decision not in ("BUY", "SELL"):
            return {
                "decision_date": decision_date,
                "decision": decision,
                "error": "decision must be BUY or SELL"
            }

        try:
            rec = self.loader.fetch_next_close(decision_date)

            if rec["next_close"] is None:
                return {
                    "decision_date": decision_date,
                    "decision": decision,
                    "error": "no next close available"
                }

            price_then = rec["close"]
            price_next = rec["next_close"]
            return_pct = (price_next - price_then) / price_then

            # Check if decision was correct
            correct = (decision == "BUY" and return_pct > 0) or \
                      (decision == "SELL" and return_pct < 0)

            return BacktestResult(
                decision_date=rec["date"],
                decision=decision,
                price_then=float(price_then),
                price_next=float(price_next),
                next_date=rec["next_date"],
                return_pct=float(return_pct),
                correct=bool(correct)
            ).model_dump()

        except Exception as e:
            logger.error(f"Error evaluating {decision_date}: {e}")
            return {
                "decision_date": decision_date,
                "decision": decision,
                "error": str(e)
            }

    def evaluate_batch(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Evaluate multiple decisions from CSV.

        Args:
            df: DataFrame with 'date' and 'decision' columns

        Returns:
            DataFrame with evaluation results
        """
        records = []

        for _, row in df.iterrows():
            date = str(row["date"])
            decision = str(row["decision"])

            result = self.evaluate_single_decision(date, decision)
            records.append(result)

            # Rate limiting for Binance API
            time.sleep(0.1)

        return pd.DataFrame(records)

    def summarize_results(self, results_df: pd.DataFrame) -> Dict:
        """Compute aggregate statistics."""
        # Filter out error rows
        if "error" in results_df.columns:
            valid = results_df[results_df["error"].isna()].copy()
        else:
            valid = results_df.copy()

        if valid.empty or "correct" not in valid.columns:
            return BacktestSummary(
                total=len(results_df),
                valid=0,
                errors=len(results_df),
                correct=0,
                accuracy_pct=0.0,
                avg_return_pct=0.0,
                cumulative_pnl=0.0
            ).model_dump()

        correct_decisions = valid[valid["correct"] == True]
        incorrect_decisions = valid[valid["correct"] == False]

        total_valid = len(valid)
        num_correct = len(correct_decisions)

        accuracy = (num_correct / total_valid * 100) if total_valid > 0 else 0.0
        avg_return = float(valid["return_pct"].mean() * 100) if "return_pct" in valid.columns else 0.0
        cumulative_pnl = float(valid["return_pct"].sum())

        return BacktestSummary(
            total=len(results_df),
            valid=total_valid,
            errors=len(results_df) - total_valid,
            correct=num_correct,
            accuracy_pct=round(accuracy, 2),
            avg_return_pct=round(avg_return, 4),
            cumulative_pnl=round(cumulative_pnl, 6)
        ).model_dump()


def main():
    parser = argparse.ArgumentParser(
        description="Backtest BTC BUY/SELL decisions using Binance data"
    )
    parser.add_argument("--file", "-f", help="CSV file with columns: date,decision", type=str)
    parser.add_argument("--date", "-d", help="Single decision date YYYY-MM-DD", type=str)
    parser.add_argument("--decision", help="BUY or SELL (used with --date)", type=str)
    parser.add_argument("--output", "-o", help="Save JSON results to file", type=str)

    args = parser.parse_args()

    engine = BacktestEngine()

    if args.file:
        logger.info(f"Loading decisions from {args.file}")
        df = pd.read_csv(args.file)

        if not {"date", "decision"}.issubset(df.columns):
            logger.error("CSV must contain 'date' and 'decision' columns")
            return 1

        results = engine.evaluate_batch(df)

    elif args.date and args.decision:
        logger.info(f"Evaluating single decision: {args.date} {args.decision}")
        result = engine.evaluate_single_decision(args.date, args.decision)
        results = pd.DataFrame([result])

    else:
        parser.print_help()
        return 1

    # Print results
    print("\n=== Backtest Results ===")
    print(results.to_string(index=False))

    # Compute summary
    summary = engine.summarize_results(results)
    print("\n=== Summary ===")
    for key, value in summary.items():
        print(f"  {key}: {value}")

    # Optional output file
    if args.output:
        output_path = Path(args.output)
        output_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "results": results.to_dict(orient="records"),
            "summary": summary
        }
        with open(output_path, 'w') as f:
            json.dump(output_data, f, indent=2, default=str)
        logger.info(f"Results saved to {output_path}")

    return 0


if __name__ == "__main__":
    exit(main())
