"""Pre-fetch product images and save to JSON for the dashboard."""
import json, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import pandas as pd
from utils.image_scraper import get_entity_image

SUMMARY = Path("outputs/summary_top_asins.csv")
IMAGES_JSON = Path("outputs/product_images.json")
LAST_RUN = Path("outputs/last_run.json")

def main():
    if not SUMMARY.exists():
        print("❌ No summary file. Run the pipeline first.")
        return

    df = pd.read_csv(SUMMARY)
    lr = {}
    if LAST_RUN.exists():
        try: lr = json.loads(LAST_RUN.read_text(encoding="utf-8"))
        except: pass
    etype = "yelp" if lr.get("dataset") == "yelp" else "product"

    # Load existing cache
    existing = {}
    if IMAGES_JSON.exists():
        try: existing = json.loads(IMAGES_JSON.read_text(encoding="utf-8"))
        except: pass

    names = df["name"].dropna().unique().tolist()
    print(f"📷 Fetching images for {len(names)} products...")

    for i, name in enumerate(names):
        name = str(name).strip()
        if not name or name in existing:
            continue
        print(f"  [{i+1}/{len(names)}] {name[:50]}...")
        url = get_entity_image(name, etype)
        if url:
            existing[name] = url
            print(f"    ✅ Got image")
        else:
            existing[name] = ""
            print(f"    ⚠️ No image found")

    IMAGES_JSON.write_text(json.dumps(existing, indent=2), encoding="utf-8")
    found = sum(1 for v in existing.values() if v)
    print(f"\n✅ Done! {found}/{len(existing)} products have images.")
    print(f"   Saved to {IMAGES_JSON}")

if __name__ == "__main__":
    main()
