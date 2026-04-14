import argparse
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path


def parse_args():
    p = argparse.ArgumentParser(description="Run TrustLens+ pipeline.")
    p.add_argument("--dataset", choices=["amazon", "yelp"], default="amazon")
    p.add_argument("--input", dest="input_path", default=None)
    p.add_argument("--max-rows", type=int, default=None)
    p.add_argument("--date-start", default=None)
    p.add_argument("--date-end", default=None)
    p.add_argument("--business-ids-file", default=None)
    p.add_argument(
        "--max-entities",
        type=int,
        default=None,
        help="Limit entities processed in reporting/plotting for faster runs.",
    )
    p.add_argument(
        "--skip-figures",
        action="store_true",
        help="Skip saving PNG figures in reporting step.",
    )
    return p.parse_args()


def run(cmd):
    print("\n▶", " ".join(cmd))
    r = subprocess.run([sys.executable] + cmd)
    if r.returncode != 0:
        raise SystemExit("Step failed.")


def main():
    t0 = time.perf_counter()
    args = parse_args()

    step1 = ["src/01_load_and_clean.py", "--dataset", args.dataset]
    if args.input_path:
        step1 += ["--input", args.input_path]
    if args.max_rows is not None:
        step1 += ["--max-rows", str(args.max_rows)]
    if args.date_start:
        step1 += ["--date-start", args.date_start]
    if args.date_end:
        step1 += ["--date-end", args.date_end]
    if args.business_ids_file:
        step1 += ["--business-ids-file", args.business_ids_file]

    run(step1)
    run(["src/02_features_and_detection.py"])
    step3 = ["src/03_reporting_and_plots.py"]
    if args.max_entities is not None and args.max_entities > 0:
        step3 += ["--max-entities", str(args.max_entities)]
    if args.skip_figures:
        step3 += ["--skip-figures"]

    run(step3)

    elapsed = round(time.perf_counter() - t0, 2)
    run_meta = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "seconds": elapsed,
        "dataset": args.dataset,
        "input": args.input_path,
        "max_rows": args.max_rows,
        "date_start": args.date_start,
        "date_end": args.date_end,
        "business_ids_file": args.business_ids_file,
        "max_entities": args.max_entities,
        "skip_figures": args.skip_figures,
    }

    out_path = Path("outputs/last_run.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(run_meta, indent=2), encoding="utf-8")

    print(f"Pipeline runtime: {elapsed} seconds")
    print("\n✅ TrustLens+ pipeline complete.")


if __name__ == "__main__":
    main()
