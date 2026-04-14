import os
import argparse
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

FEATURES_OUT = "outputs/weekly_features.csv"
CLEAN_PATH = "outputs/cleaned_reviews.csv"
SUMMARY_OUT = "outputs/summary_top_asins.csv"
FIG_DIR = "outputs/figures"

os.makedirs(FIG_DIR, exist_ok=True)


def parse_args():
    p = argparse.ArgumentParser(description="Build summary and optional plots from weekly features.")
    p.add_argument("--max-entities", type=int, default=None)
    p.add_argument("--skip-figures", action="store_true")
    return p.parse_args()

def badge(score):
    if score >= 70: return "High"
    if score >= 40: return "Medium"
    return "Low"

def main():
    args = parse_args()
    wf = pd.read_csv(FEATURES_OUT)
    wf["week"] = pd.to_datetime(wf["week"], errors="coerce", utc=True, format="mixed")

    df = pd.read_csv(CLEAN_PATH)
    df["reviews.date"] = pd.to_datetime(df["reviews.date"], errors="coerce", utc=True, format="mixed")

    summary = []
    grouped = list(df.groupby("asins"))
    grouped.sort(key=lambda kv: len(kv[1]), reverse=True)
    if args.max_entities is not None and args.max_entities > 0:
        grouped = grouped[: args.max_entities]

    for asin, block in grouped:
        w = wf[wf["asins"] == asin].sort_values("week")
        if w.empty:
            continue

        safe_asin = (
            str(asin)
            .replace("\"", "")
            .replace(",", "_")
            .replace("/", "_")
            .replace("\\", "_")
            .strip()
        )

        suspicious_weeks = w.loc[w["suspicious"] == True, "week"].tolist()

        observed = float(block["reviews.rating"].mean())
        block2 = block.copy()
        block2["week"] = block2["reviews.date"].dt.floor("7D")
        kept = block2[~block2["week"].isin(set(suspicious_weeks))]["reviews.rating"]
        fair = float(kept.mean()) if len(kept) else observed
        distortion = observed - fair

        overall_trust = float(np.nanmean(w["trust_score"])) if w["trust_score"].notna().any() else 100.0
        entity_name = str(block["name"].iloc[0]) if "name" in block.columns else str(asin)
        entity_city = str(block["city"].iloc[0]) if "city" in block.columns and block["city"].iloc[0] else ""
        entity_state = str(block["state"].iloc[0]) if "state" in block.columns and block["state"].iloc[0] else ""
        
        summary.append({
            "asins": asin,
            "name": entity_name,
            "city": entity_city,
            "state": entity_state,
            "reviews": len(block),
            "weeks": len(w),
            "suspicious_weeks": int(w["suspicious"].sum()),
            "observed_rating": round(observed, 3),
            "fair_rating": round(fair, 3),
            "distortion": round(distortion, 3),
            "overall_trust": round(overall_trust, 2),
            "badge": badge(overall_trust)
        })

        if not args.skip_figures:
            # plots
            s = w[w["suspicious"] == True]
            plt.figure()
            plt.plot(w["week"], w["review_count"])
            if len(s): plt.scatter(s["week"], s["review_count"])
            plt.title(f"{asin} - Reviews per Week")
            plt.xlabel("Week"); plt.ylabel("Review count")
            plt.savefig(os.path.join(FIG_DIR, f"{safe_asin}_reviews.png"), bbox_inches="tight")
            plt.close()

            plt.figure()
            plt.plot(w["week"], w["avg_rating"])
            if len(s): plt.scatter(s["week"], s["avg_rating"])
            plt.title(f"{asin} - Avg Rating Over Time")
            plt.xlabel("Week"); plt.ylabel("Avg rating")
            plt.savefig(os.path.join(FIG_DIR, f"{safe_asin}_rating.png"), bbox_inches="tight")
            plt.close()

            plt.figure()
            plt.plot(w["week"], w["trust_score"])
            if len(s): plt.scatter(s["week"], s["trust_score"])
            plt.title(f"{asin} - Trust Score Timeline")
            plt.xlabel("Week"); plt.ylabel("Trust score")
            plt.savefig(os.path.join(FIG_DIR, f"{safe_asin}_trust.png"), bbox_inches="tight")
            plt.close()

    out = pd.DataFrame(summary).sort_values(["suspicious_weeks", "distortion"], ascending=False)
    out.to_csv(SUMMARY_OUT, index=False)
    print("✅ Summary saved:", SUMMARY_OUT)
    print("Entities processed:", len(out))
    print(out.head(15).to_string(index=False))
    if args.skip_figures:
        print("ℹ Figures were skipped (--skip-figures).")
    else:
        print("✅ Figures saved in:", FIG_DIR)

if __name__ == "__main__":
    main()
