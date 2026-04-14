import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

CLEAN_PATH = "outputs/cleaned_reviews.csv"
FEATURES_OUT = "outputs/weekly_features.csv"

WINDOW = "7D"
SPIKE_THR = 0.7
TEXT_SIM_THR = 0.20
UNIQUE_RATIO_THR = 0.70
BURST_STD_MULT = 1.5

MIN_SIM_REVIEWS = 5
MAX_DOCS_FOR_SIM = 80

def avg_pairwise_similarity(texts):
    if len(texts) < 2:
        return np.nan
    vec = TfidfVectorizer(stop_words="english", max_features=5000)
    X = vec.fit_transform(texts)
    sims = cosine_similarity(X)
    tri = sims[np.triu_indices_from(sims, k=1)]
    return float(np.mean(tri)) if tri.size else np.nan

def compute_weekly_features(df_asin):
    d = df_asin.sort_values("reviews.date").copy()
    d["week"] = d["reviews.date"].dt.floor(WINDOW)
    grp = d.groupby("week")

    out = grp.agg(
        review_count=("reviews.rating", "size"),
        avg_rating=("reviews.rating", "mean"),
        rating_std=("reviews.rating", "std"),
        unique_users=("reviews.username", pd.Series.nunique),
        pct_5=("reviews.rating", lambda x: (x == 5).mean()),
        pct_1=("reviews.rating", lambda x: (x == 1).mean()),
    ).reset_index()

    out["unique_ratio"] = out["unique_users"] / out["review_count"]

    # text similarity per week
    sim_scores = []
    for _, block in grp:
        texts = (block["reviews.title"].astype(str) + " " + block["reviews.text"].astype(str)).tolist()
        if len(texts) < MIN_SIM_REVIEWS:
            sim_scores.append(np.nan)
            continue
        if len(texts) > MAX_DOCS_FOR_SIM:
            texts = texts[:MAX_DOCS_FOR_SIM]
        sim_scores.append(avg_pairwise_similarity(texts))

    out["avg_text_sim"] = sim_scores
    return out.sort_values("week")

def detect(wf):
    x = wf.copy()
    mu = x["review_count"].mean()
    sd = x["review_count"].std(ddof=0)
    burst_thr = mu + BURST_STD_MULT * sd

    x["burst_flag"] = x["review_count"] > burst_thr
    x["prev_avg"] = x["avg_rating"].shift(1)
    x["rating_change"] = (x["avg_rating"] - x["prev_avg"]).abs().fillna(0.0)
    x["spike_flag"] = x["rating_change"] >= SPIKE_THR
    x["text_flag"] = x["avg_text_sim"].fillna(0) >= TEXT_SIM_THR
    x["user_flag"] = x["unique_ratio"] < UNIQUE_RATIO_THR

    x["flag_count"] = x[["burst_flag", "spike_flag", "text_flag", "user_flag"]].sum(axis=1)
    x["suspicious"] = x["flag_count"] >= 2

    # scores
    x["burst_score"] = np.clip((x["review_count"] - mu) / (sd + 1e-9), 0, 3) / 3
    x["spike_score"] = np.clip(x["rating_change"] / 2, 0, 1).fillna(0.0)
    x["text_score"] = np.clip(x["avg_text_sim"].fillna(0) / 0.6, 0, 1)
    x["user_score"] = np.clip((UNIQUE_RATIO_THR - x["unique_ratio"]) / UNIQUE_RATIO_THR, 0, 1)

    x["S"] = (
        0.35 * x["burst_score"]
        + 0.25 * x["spike_score"]
        + 0.25 * x["text_score"]
        + 0.15 * x["user_score"]
    ).fillna(0.0)
    x["trust_score"] = 100 * (1 - np.clip(x["S"], 0, 1))
    x["burst_threshold"] = burst_thr
    return x

def main():
    df = pd.read_csv(CLEAN_PATH)
    df["reviews.date"] = pd.to_datetime(df["reviews.date"], errors="coerce", utc=True, format="mixed")

    all_rows = []
    for asin, block in df.groupby("asins"):
        wf = compute_weekly_features(block)
        wf = detect(wf)
        wf["asins"] = asin
        all_rows.append(wf)

    out = pd.concat(all_rows, ignore_index=True)
    out.to_csv(FEATURES_OUT, index=False)
    print("✅ Weekly features saved:", FEATURES_OUT)
    print(out.head(3))

if __name__ == "__main__":
    main()
