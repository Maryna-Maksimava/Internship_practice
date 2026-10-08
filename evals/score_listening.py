"""Join the human rating sheet with the blinding key and average per engine.

    python evals/score_listening.py [evals/results/listening_sheet_short.csv]
"""
import csv
import pathlib
import statistics
import sys

RESULTS = pathlib.Path(__file__).resolve().parent / "results"


def read(path):
    with open(path, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def main():
    sheet = read(sys.argv[1] if len(sys.argv) > 1 else RESULTS / "listening_sheet_short.csv")
    key = {k["clip"]: k for k in read(RESULTS / "listening_key.csv")}
    stats = {}
    unrated = 0
    for r in sheet:
        score = (r.get("naturalness_1_5") or "").strip()
        if not score:
            unrated += 1
            continue
        e = key[r["clip"]]["engine"]
        s = stats.setdefault(e, {"nat": [], "pause": 0, "misread": 0, "n": 0})
        s["nat"].append(float(score)); s["n"] += 1
        s["pause"] += (r.get("odd_pause_y_n") or "").strip().lower() == "y"
        s["misread"] += (r.get("misread_y_n") or "").strip().lower() == "y"
    print(f"rated {sum(s['n'] for s in stats.values())} clips, {unrated} unrated\n")
    print("| Engine | Rated | Mean naturalness (1-5) | Odd pause | Misread |")
    print("|---|---|---|---|---|")
    for e, s in sorted(stats.items(), key=lambda kv: -statistics.mean(kv[1]["nat"])):
        print(f"| {e} | {s['n']} | {statistics.mean(s['nat']):.2f} | {s['pause']}/{s['n']} | {s['misread']}/{s['n']} |")


if __name__ == "__main__":
    main()
