import argparse
from pathlib import Path

import pandas as pd

DEFAULT_AMAZON_INPUT = "data/7817_1.csv"
DEFAULT_YELP_INPUT = "../dataset/yelp/yelp_academic_dataset_review.json"
OUTPUT_PATH = "outputs/cleaned_reviews.csv"

NORMALIZED_COLS = [
    "asins",
    "reviews.date",
    "reviews.rating",
    "reviews.text",
    "reviews.title",
    "reviews.username",
    "reviews.numHelpful",
    "reviews.doRecommend",
    "name",
    "city",
    "state",
]


def parse_args():
    p = argparse.ArgumentParser(description="Load and clean reviews (Amazon CSV or Yelp JSONL).")
    p.add_argument("--dataset", choices=["amazon", "yelp"], default="amazon")
    p.add_argument("--input", dest="input_path", default=None)
    p.add_argument("--output", dest="output_path", default=OUTPUT_PATH)
    p.add_argument("--max-rows", type=int, default=None, help="Keep at most N rows after cleaning.")
    p.add_argument("--date-start", default=None, help="Inclusive date lower bound (YYYY-MM-DD).")
    p.add_argument("--date-end", default=None, help="Inclusive date upper bound (YYYY-MM-DD).")
    p.add_argument(
        "--business-ids-file",
        default=None,
        help="Optional text file with Yelp business_id values (one per line).",
    )
    return p.parse_args()


def normalize_common(df: pd.DataFrame) -> pd.DataFrame:
    for c in NORMALIZED_COLS:
        if c not in df.columns:
            df[c] = pd.NA

    df = df[NORMALIZED_COLS].copy()
    df["reviews.date"] = pd.to_datetime(df["reviews.date"], errors="coerce", utc=True)
    df["reviews.rating"] = pd.to_numeric(df["reviews.rating"], errors="coerce")

    df = df.dropna(subset=["asins", "reviews.date", "reviews.rating"])
    df["asins"] = df["asins"].astype(str).str.strip()
    df = df[df["asins"] != ""]

    df["reviews.text"] = df["reviews.text"].fillna("").astype(str)
    df["reviews.title"] = df["reviews.title"].fillna("").astype(str)
    df["reviews.username"] = df["reviews.username"].fillna("unknown").astype(str)
    
    if "name" not in df.columns or df["name"].isna().all():
        df["name"] = df["asins"]
    df["name"] = df["name"].fillna(df["asins"]).astype(str)
    
    if "city" not in df.columns:
        df["city"] = ""
    df["city"] = df["city"].fillna("").astype(str)
    
    if "state" not in df.columns:
        df["state"] = ""
    df["state"] = df["state"].fillna("").astype(str)

    return df


def load_amazon_csv(input_path: str) -> pd.DataFrame:
    print("📖 Loading Amazon CSV from:", input_path)
    df = pd.read_csv(input_path, encoding="utf-8", encoding_errors="replace", low_memory=False)
    return normalize_common(df)


def _read_business_filter(path: str | None) -> set[str] | None:
    if not path:
        return None
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"business IDs file not found: {path}")
    values = {line.strip() for line in p.read_text(encoding="utf-8").splitlines() if line.strip()}
    return values if values else None


def load_yelp_jsonl(input_path: str, business_ids_file: str | None = None) -> pd.DataFrame:
    print("📖 Loading Yelp JSONL from:", input_path)
    keep_ids = _read_business_filter(business_ids_file)

    chunks = []
    for chunk in pd.read_json(input_path, lines=True, chunksize=100000):
        mapped = pd.DataFrame(
            {
                "asins": chunk.get("business_id"),
                "reviews.date": chunk.get("date"),
                "reviews.rating": chunk.get("stars"),
                "reviews.text": chunk.get("text"),
                "reviews.title": "",
                "reviews.username": chunk.get("user_id"),
                "reviews.numHelpful": chunk.get("useful"),
                "reviews.doRecommend": pd.NA,
                "name": pd.NA,
            }
        )

        if keep_ids is not None:
            mapped = mapped[mapped["asins"].astype(str).isin(keep_ids)]

        if not mapped.empty:
            chunks.append(mapped)

    if not chunks:
        return pd.DataFrame(columns=NORMALIZED_COLS)

    df = pd.concat(chunks, ignore_index=True)
    
    # Try to load business names
    bus_path = Path(input_path).parent / "yelp_academic_dataset_business.json"
    if not bus_path.exists():
        bus_path = Path("yelp_academic_dataset_business.json")
        
    if bus_path.exists():
        print("📖 Loading Yelp Business JSON for names and locations...")
        try:
            b_df = pd.read_json(bus_path, lines=True)
            if "business_id" in b_df.columns:
                if "name" in b_df.columns:
                    name_map = b_df.set_index("business_id")["name"].to_dict()
                    df["name"] = df["asins"].map(name_map)
                if "city" in b_df.columns:
                    city_map = b_df.set_index("business_id")["city"].to_dict()
                    df["city"] = df["asins"].map(city_map)
                if "state" in b_df.columns:
                    state_map = b_df.set_index("business_id")["state"].to_dict()
                    df["state"] = df["asins"].map(state_map)
        except Exception as e:
            print(f"⚠️ Could not load business data: {e}")

    return normalize_common(df)


def apply_filters(df: pd.DataFrame, date_start: str | None, date_end: str | None, max_rows: int | None) -> pd.DataFrame:
    if date_start:
        start_ts = pd.to_datetime(date_start, errors="coerce", utc=True)
        if pd.notna(start_ts):
            df = df[df["reviews.date"] >= start_ts]

    if date_end:
        end_ts = pd.to_datetime(date_end, errors="coerce", utc=True)
        if pd.notna(end_ts):
            df = df[df["reviews.date"] <= end_ts]

    if max_rows is not None and max_rows > 0:
        df = df.head(max_rows)

    return df


def dedupe_and_sort(df: pd.DataFrame) -> pd.DataFrame:
    df = df.drop_duplicates(
        subset=["asins", "reviews.username", "reviews.date", "reviews.rating", "reviews.text"]
    )
    return df.sort_values(["asins", "reviews.date"]).reset_index(drop=True)


def main():
    args = parse_args()
    input_path = args.input_path or (DEFAULT_YELP_INPUT if args.dataset == "yelp" else DEFAULT_AMAZON_INPUT)

    if args.dataset == "yelp":
        df = load_yelp_jsonl(input_path, business_ids_file=args.business_ids_file)
    else:
        df = load_amazon_csv(input_path)

    df = apply_filters(df, date_start=args.date_start, date_end=args.date_end, max_rows=args.max_rows)
    df = dedupe_and_sort(df)

    Path(args.output_path).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.output_path, index=False)

    print("✅ Cleaned data saved:", args.output_path)
    print("Dataset mode:", args.dataset)
    print("Rows:", len(df), "Columns:", len(df.columns))
    print(df.head(3))


if __name__ == "__main__":
    main()
