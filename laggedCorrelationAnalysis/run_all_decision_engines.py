"""Run all BTC decision engines and aggregate their signals by majority vote.

Usage:
    python run_all_decision_engines.py [path/to/lagged_correlation_output_summary.txt]

This script imports the available decision engine modules in this folder,
runs them against the same input file, normalizes their BUY/SELL outputs,
and prints each engine's result plus the aggregated majority vote.
"""
from pathlib import Path
from collections import Counter
import json

DEFAULT_PATH = Path("OutputLaggedCorrelationAnalysis/lagged_correlation_output_summary.txt")


def normalize_signal(raw: str) -> str:
    if not raw or not isinstance(raw, str):
        return "UNKNOWN"
    s = raw.upper()
    if "BUY" in s:
        return "BUY"
    if "SELL" in s:
        return "SELL"
    return "UNKNOWN"


def run_all(input_path: Path):
    input_path = Path(input_path)
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    text = input_path.read_text(encoding="utf-8")

    results = {}

    # ChatGPT engine: expects main(file_path)
    try:
        from ChatGPTBTCLaggedCorrelationDecisionEngine import main as chatgpt_main

        sig, info = chatgpt_main(str(input_path))
        results["ChatGPT"] = {"raw": sig, "normalized": normalize_signal(sig)}
    except Exception as e:
        results["ChatGPT"] = {"error": str(e)}

    # Claude engine: use BTCSignalGenerator.analyze(file_path)
    try:
        from ClaudeBTCLaggedCorrelationDecisionEngine import BTCSignalGenerator

        gen = BTCSignalGenerator(verbose=False)
        res = gen.analyze(str(input_path), is_filepath=True)
        sig = res.signal if hasattr(res, "signal") else getattr(res, "signal", None)
        results["Claude"] = {"raw": sig, "normalized": normalize_signal(sig), "confidence": getattr(res, "confidence", None)}
    except Exception as e:
        results["Claude"] = {"error": str(e)}

    # Copilot engine: main(argv=None) -> returns (signal, result)
    try:
        from CopilotBTCLaggedCorrelationDecisionEngine import main as copilot_main

        sig, info = copilot_main([str(input_path)])
        results["Copilot"] = {"raw": sig, "normalized": normalize_signal(sig), "info": info}
    except Exception as e:
        results["Copilot"] = {"error": str(e)}

    # Gemin engine: main(input_text) expects raw text
    try:
        from GeminBTCLaggedCorrelationDecisionEngine import main as gemin_main

        sig, info = gemin_main(text)
        results["Gemin"] = {"raw": sig, "normalized": normalize_signal(sig), "info": info}
    except Exception as e:
        results["Gemin"] = {"error": str(e)}

    # Perplexity engine: main(input_path) -> returns (signal, info)
    try:
        from PerplexityBTCLaggedCorrelationDecisionEngine import main as perplexity_main

        sig, info = perplexity_main(str(input_path))
        results["Perplexity"] = {"raw": sig, "normalized": normalize_signal(sig), "info": info}
    except Exception as e:
        results["Perplexity"] = {"error": str(e)}

    return results


def aggregate(results: dict) -> dict:
    votes = []
    for k, v in results.items():
        if isinstance(v, dict) and "normalized" in v:
            votes.append(v["normalized"])

    counts = Counter(votes)
    if not counts:
        majority = "NO_RESULT"
    else:
        most_common = counts.most_common()
        # check top two for tie
        if len(most_common) > 1 and most_common[0][1] == most_common[1][1]:
            majority = "TIE"
        else:
            majority = most_common[0][0]

    return {"votes": counts, "majority": majority}


def print_report(results: dict, agg: dict):
    print("=== Individual Engine Results ===")
    for engine, res in results.items():
        if "error" in res:
            print(f"- {engine}: ERROR -> {res['error']}")
            continue
        raw = res.get("raw")
        norm = res.get("normalized")
        conf = res.get("confidence") or (res.get("info") and res.get("info").get("confidence"))
        print(f"- {engine}: raw={raw} normalized={norm} confidence={conf}")

    print()
    print("=== Aggregated Vote ===")
    print(f"Votes: {json.dumps({k: v for k, v in agg['votes'].items()})}")
    print(f"Majority decision: {agg['majority']}")


def main():
    import sys

    path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_PATH
    try:
        results = run_all(path)
        agg = aggregate(results)
        print_report(results, agg)
    except Exception as e:
        print(f"Error running aggregation: {e}")
        
    # return BUY or SELL majority and detailed results for potential further use
    # return agg['majority'], results, agg


if __name__ == "__main__":
    main()
