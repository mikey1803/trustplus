"""
Extract product metadata (prices, links, image URLs) from Amazon dataset
and add to the summary CSV. Uses ASIN-based Amazon image URLs.
"""
import json, re, ast
from pathlib import Path
import pandas as pd

CSV_INPUT = Path("data/7817_1.csv")
SUMMARY = Path("outputs/summary_top_asins.csv")
USD_TO_INR = 83.50

def extract_price(price_str):
    """Extract price from the JSON-like prices column."""
    if pd.isna(price_str) or not str(price_str).strip():
        return None
    try:
        s = str(price_str)
        # Find amountMax or amountMin
        match = re.search(r'"amountMax"\s*:\s*([\d.]+)', s)
        if match:
            return float(match.group(1))
        match = re.search(r'"amountMin"\s*:\s*([\d.]+)', s)
        if match:
            return float(match.group(1))
    except:
        pass
    return None

def extract_source_url(url_str):
    """Extract Amazon product URL."""
    if pd.isna(url_str) or not str(url_str).strip():
        return ""
    s = str(url_str)
    match = re.search(r'(https?://www\.amazon\.com/[^\s,\]"]+)', s)
    if match:
        return match.group(1)
    return ""

def asin_to_image_url(asins_str):
    """Build Amazon product image URL from ASIN."""
    if pd.isna(asins_str):
        return ""
    asin = str(asins_str).split(",")[0].strip()
    if asin and len(asin) == 10:
        return f"https://images-na.ssl-images-amazon.com/images/P/{asin}.01._SCLZZZZZZZ_.jpg"
    return ""

def main():
    if not CSV_INPUT.exists() or not SUMMARY.exists():
        print("❌ Missing files"); return

    print("📦 Loading Amazon dataset...")
    raw = pd.read_csv(CSV_INPUT, low_memory=False)

    # Get unique products with first occurrence of metadata
    products = raw.groupby("asins").agg({
        "name": "first",
        "prices": "first",
        "reviews.sourceURLs": "first",
    }).reset_index()

    products["price_usd"] = products["prices"].apply(extract_price)
    products["price_inr"] = products["price_usd"].apply(lambda x: round(x * USD_TO_INR) if pd.notna(x) else None)
    products["product_url"] = products["reviews.sourceURLs"].apply(extract_source_url)
    products["image_url"] = products["asins"].apply(asin_to_image_url)

    # Merge with summary
    summary = pd.read_csv(SUMMARY)
    for col in ["price_usd", "price_inr", "product_url", "image_url"]:
        if col in summary.columns:
            summary = summary.drop(columns=[col])

    merged = summary.merge(
        products[["asins", "price_usd", "price_inr", "product_url", "image_url"]],
        on="asins", how="left"
    )

    merged.to_csv(SUMMARY, index=False)

    has_price = merged["price_inr"].notna().sum()
    has_url = (merged["product_url"].str.strip() != "").sum()
    has_img = (merged["image_url"].str.strip() != "").sum()
    print(f"✅ Updated summary: {has_price} with prices, {has_url} with URLs, {has_img} with images")
    print(f"   Sample image: {merged['image_url'].iloc[0]}")
    print(f"   Sample price: ₹{merged['price_inr'].iloc[0]}")

if __name__ == "__main__":
    main()
