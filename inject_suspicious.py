"""
Inject suspicious review patterns into the Amazon dataset to demonstrate
TrustLens+ manipulation detection capabilities.

Creates realistic-looking manipulation patterns:
- Review bursts (many reviews in short time windows)
- Rating spikes (sudden rating inflation)
- Similar/copy-paste review text
- Fake account patterns (low unique reviewers)
"""
import pandas as pd
import numpy as np
import random
import string
from datetime import datetime, timedelta

INPUT = "data/7817_1.csv"
OUTPUT = "data/7817_1.csv"  # overwrite with enriched data

# Target products to inject suspicious reviews into
TARGETS = [
    "All-New Amazon Fire TV Game Controller",
    "Amazon Tap - Alexa-Enabled Portable Bluetooth Speaker",
    "Kindle Voyage E-reader",
]

FAKE_POSITIVE_REVIEWS = [
    "This is absolutely the best product I have ever purchased! Amazing quality and fast shipping. Highly recommend to everyone!",
    "Incredible product! Works perfectly and exceeded all my expectations. Best purchase this year hands down!",
    "Outstanding quality! I bought this for my family and everyone loves it. Five stars all the way!",
    "Amazing product, works exactly as described. The quality is top notch and delivery was super fast!",
    "Best product in this category! I've tried many alternatives but nothing comes close to this one!",
    "Wow just wow! This product changed my life. I can't believe how good it is for the price!",
    "Perfect in every way! The build quality is exceptional and it works flawlessly. Buy this now!",
    "Absolutely love this product! Have been using it daily and it never disappoints. Highly recommended!",
    "This is exactly what I was looking for! Great quality, great price, great product overall!",
    "Five stars! This product is amazing. I bought three more as gifts for my friends and family!",
]

FAKE_NEGATIVE_REVIEWS = [
    "Terrible product. Broke after one day. Complete waste of money. Do not buy this garbage.",
    "Worst purchase ever. Nothing works as described. Total scam product. Want my money back.",
    "Absolutely horrible. The quality is non-existent. Feels like a cheap knockoff. Avoid at all costs.",
]

FAKE_USERNAMES = [
    "HappyBuyer123", "ProductFan99", "ReviewerX42", "BestDeals2024",
    "TopReviewer88", "QualityCheck77", "SmartShopper56", "DealHunter33",
    "TechLover2024", "GadgetGuru99", "PrimeUser101", "FastShipper55",
]

def inject_burst_reviews(df, product_name, burst_date, count=15):
    """Inject a burst of suspiciously positive reviews in a short window."""
    rows = []
    asin = df[df["name"] == product_name]["asins"].iloc[0] if product_name in df["name"].values else None
    if asin is None:
        print(f"⚠️ Product '{product_name}' not found, skipping")
        return pd.DataFrame()

    for i in range(count):
        dt = burst_date + timedelta(hours=random.randint(0, 48))
        rows.append({
            "asins": asin,
            "name": product_name,
            "reviews.date": dt.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
            "reviews.rating": 5,
            "reviews.text": random.choice(FAKE_POSITIVE_REVIEWS),
            "reviews.title": random.choice([
                "Amazing!", "Best ever!", "Love it!", "Perfect!",
                "Incredible!", "Must buy!", "Outstanding!", "Fantastic!"
            ]),
            "reviews.username": random.choice(FAKE_USERNAMES),
            "reviews.numHelpful": random.randint(0, 2),
            "reviews.doRecommend": True,
            "city": "",
            "state": "",
        })
    return pd.DataFrame(rows)


def inject_rating_spike(df, product_name, spike_date, count=10):
    """Inject reviews that create an artificial rating spike."""
    rows = []
    asin = df[df["name"] == product_name]["asins"].iloc[0] if product_name in df["name"].values else None
    if asin is None:
        return pd.DataFrame()

    # Add some low ratings before the spike
    for i in range(3):
        dt = spike_date - timedelta(days=random.randint(7, 14))
        rows.append({
            "asins": asin, "name": product_name,
            "reviews.date": dt.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
            "reviews.rating": random.choice([1, 2, 2, 3]),
            "reviews.text": random.choice(FAKE_NEGATIVE_REVIEWS),
            "reviews.title": "Disappointed",
            "reviews.username": f"RealUser{random.randint(1000,9999)}",
            "reviews.numHelpful": random.randint(0, 5),
            "reviews.doRecommend": False,
            "city": "", "state": "",
        })

    # Then a sudden spike of 5-star reviews
    for i in range(count):
        dt = spike_date + timedelta(hours=random.randint(0, 72))
        rows.append({
            "asins": asin, "name": product_name,
            "reviews.date": dt.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
            "reviews.rating": 5,
            "reviews.text": random.choice(FAKE_POSITIVE_REVIEWS),
            "reviews.title": random.choice(["Perfect!", "Love it!", "Best ever!", "Amazing!"]),
            "reviews.username": random.choice(FAKE_USERNAMES[:4]),  # few unique users
            "reviews.numHelpful": 0,
            "reviews.doRecommend": True,
            "city": "", "state": "",
        })
    return pd.DataFrame(rows)


def inject_copycat_reviews(df, product_name, date, count=8):
    """Inject nearly identical reviews (text similarity flag)."""
    rows = []
    asin = df[df["name"] == product_name]["asins"].iloc[0] if product_name in df["name"].values else None
    if asin is None:
        return pd.DataFrame()

    # Use the SAME review text with tiny variations
    base_text = "This is absolutely the best product I have ever purchased! Amazing quality and fast shipping. Highly recommend to everyone!"
    variations = [
        base_text,
        base_text.replace("purchased", "bought"),
        base_text.replace("Amazing", "Incredible").replace("everyone", "all"),
        base_text.replace("best product", "greatest product").replace("Highly", "Strongly"),
        base_text + " Will buy again!",
        "Best product ever! " + base_text[20:],
        base_text.replace("fast shipping", "quick delivery"),
        base_text.replace("ever purchased", "ever used"),
    ]

    for i in range(count):
        dt = date + timedelta(hours=random.randint(0, 24))
        rows.append({
            "asins": asin, "name": product_name,
            "reviews.date": dt.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
            "reviews.rating": 5,
            "reviews.text": variations[i % len(variations)],
            "reviews.title": "Great product!",
            "reviews.username": random.choice(FAKE_USERNAMES),
            "reviews.numHelpful": 0,
            "reviews.doRecommend": True,
            "city": "", "state": "",
        })
    return pd.DataFrame(rows)


def main():
    print("📦 Loading Amazon dataset...")
    df = pd.read_csv(INPUT, low_memory=False)
    print(f"   Original: {len(df)} reviews")

    injected = []

    # Target 1: Burst + copycat reviews
    if TARGETS[0] in df["name"].values:
        print(f"💉 Injecting burst + copycat into '{TARGETS[0]}'")
        injected.append(inject_burst_reviews(df, TARGETS[0], datetime(2017, 3, 15), count=18))
        injected.append(inject_copycat_reviews(df, TARGETS[0], datetime(2017, 3, 16), count=10))

    # Target 2: Rating spike + burst
    if TARGETS[1] in df["name"].values:
        print(f"💉 Injecting rating spike into '{TARGETS[1]}'")
        injected.append(inject_rating_spike(df, TARGETS[1], datetime(2016, 11, 25), count=12))
        injected.append(inject_burst_reviews(df, TARGETS[1], datetime(2016, 12, 1), count=15))

    # Target 3: Copycat + fake accounts
    if TARGETS[2] in df["name"].values:
        print(f"💉 Injecting copycat reviews into '{TARGETS[2]}'")
        injected.append(inject_copycat_reviews(df, TARGETS[2], datetime(2016, 8, 10), count=12))
        injected.append(inject_burst_reviews(df, TARGETS[2], datetime(2016, 8, 12), count=10))

    if injected:
        all_injected = pd.concat([d for d in injected if not d.empty], ignore_index=True)
        # Ensure columns match
        for col in df.columns:
            if col not in all_injected.columns:
                all_injected[col] = np.nan
        all_injected = all_injected[df.columns]
        df = pd.concat([df, all_injected], ignore_index=True)
        print(f"   Injected: {len(all_injected)} suspicious reviews")

    df.to_csv(OUTPUT, index=False)
    print(f"✅ Saved enriched dataset: {len(df)} total reviews")
    print("   Now run: python main.py --dataset amazon --skip-figures")


if __name__ == "__main__":
    main()
