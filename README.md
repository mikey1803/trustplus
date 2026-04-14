# TrustLens+: Impact-Aware Detection of Coordinated Review Manipulation

**TrustLens+** is a system that analyzes online review datasets (Yelp / Amazon) to detect **coordinated manipulation patterns**, measure how ratings are distorted, and estimate how user decisions are affected.

> ⚠️ This system does **NOT** detect individual fake reviews. It focuses on **coordinated patterns** (bursts, rating spikes, text similarity, user patterns) and quantifies their **impact on user decisions**.

---

## Key Features

| Feature | Description |
|---|---|
| **Burst Detection** | Flags weeks where review volume exceeds statistical threshold |
| **Rating Spike Detection** | Identifies sudden jumps/drops in average rating |
| **Text Similarity Analysis** | Uses TF-IDF cosine similarity to find suspiciously similar reviews |
| **User Pattern Analysis** | Detects low unique-user ratios indicating potential sockpuppets |
| **Trust Score** | 0–100 composite score combining all signals |
| **Decision Impact (WOW)** | Compares observed vs. fair rating to estimate user misleading potential |

---

## Tech Stack

- **Python 3.10+**
- **Pandas / NumPy** — data processing
- **Scikit-learn** — TF-IDF vectorization & cosine similarity
- **Plotly** — interactive visualizations
- **Matplotlib** — static figure export (optional)
- **Streamlit** — web dashboard

---

## Project Structure

```
TrustLensPlus/
├── app.py                          # Streamlit dashboard (premium UI)
├── main.py                         # Pipeline orchestrator
├── requirements.txt
├── README.md
├── data/
│   └── 7817_1.csv                  # Amazon review dataset
├── src/
│   ├── 01_load_and_clean.py        # Data loading & normalization
│   ├── 02_features_and_detection.py# Feature extraction & detection
│   └── 03_reporting_and_plots.py   # Summary & figure generation
└── outputs/                        # Generated CSV/JSON/PNG files
```

---

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Streamlit app

```bash
streamlit run app.py
```

### 3. Click **🚀 Run Pipeline** in the sidebar

Choose your dataset (Amazon or Yelp), configure settings, and click run.

### Alternative: Run pipeline from CLI

```bash
python main.py --dataset amazon --max-rows 200000
python main.py --dataset yelp --input ../dataset/yelp/yelp_academic_dataset_review.json --max-rows 200000
```

---

## How It Works

### Pipeline Flow

```
Raw Data → Load & Clean → Feature Extraction → Detection → Trust Score → Visualization
```

1. **Load & Clean** (`01_load_and_clean.py`) — Reads CSV/JSONL, normalizes columns, deduplicates, sorts by date
2. **Feature Extraction** (`02_features_and_detection.py`) — Computes weekly features: review count, avg rating, rating std, unique users, text similarity (TF-IDF), and applies detection logic with configurable thresholds
3. **Reporting** (`03_reporting_and_plots.py`) — Generates summary table with trust scores, fair ratings, and optional PNG figures
4. **Dashboard** (`app.py`) — Interactive Streamlit UI with Plotly charts, trust gauges, alert cards, and decision impact analysis

### Trust Score Formula

```
S = 0.35 × burst_score + 0.25 × spike_score + 0.25 × text_score + 0.15 × user_score
trust_score = 100 × (1 – clip(S, 0, 1))
```

### Decision Impact

- **Observed rating** = mean of all reviews
- **Fair rating** = mean of reviews excluding suspicious weeks
- **Distortion** = observed − fair
- Impact categories: **Low** (< 0.2), **Moderate** (0.2–0.5), **High** (≥ 0.5)

---

## Datasets

### Amazon (default)
- File: `data/7817_1.csv`
- Fields: `asins`, `reviews.date`, `reviews.rating`, `reviews.text`, `reviews.username`, etc.

### Yelp
- File: JSONL format (`yelp_academic_dataset_review.json`)
- Fields: `business_id`, `date`, `stars`, `text`, `user_id`

---

## Dashboard Sections

1. **Business Selector** — Dropdown with trust badge and review count
2. **Key Metrics** — Reviews, Suspicious Weeks, Observed Rating, Fair Rating, Distortion
3. **Trust Score** — Animated gauge with status badge
4. **Review Activity** — Bar chart with burst threshold line
5. **Rating Timeline** — Area chart with suspicious week markers
6. **Trust Score Timeline** — Line chart with colored trust zones
7. **Detection Results** — Styled alert cards + expandable detail table
8. **Decision Impact** — Side-by-side observed vs. fair rating gauges with impact narrative

---

## License

Academic / Educational use.

---

## Repository

This project is hosted at `https://github.com/mikey1803/trustplus`.
