import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

FILE = "data/7817_1.csv"

# Real ASINs with Real Image coverage on amazon servers
PRODUCTS = [
    {"asins": "B0CHX2F5QT", "name": "Apple iPhone 15 Pro Max (256 GB) - Natural Titanium", "price": "159900", "brand": "Apple"},
    {"asins": "B09XS7JWHH", "name": "Sony WH-1000XM5 Wireless Noise Canceling Headphones", "price": "29990", "brand": "Sony"},
    {"asins": "B0CQPTN5XF", "name": "Samsung Galaxy S24 Ultra 5G (Titanium Gray, 12GB, 256GB)", "price": "129999", "brand": "Samsung"},
    {"asins": "B0982GYG59", "name": "Bose Smart Soundbar 900 Dolby Atmos", "price": "89900", "brand": "Bose"},
    {"asins": "B0CRWBRSBD", "name": "ASUS ROG Zephyrus G14 Gaming Laptop", "price": "189990", "brand": "ASUS"},
    {"asins": "B0CG7PXYH4", "name": "GoPro HERO12 Black - Waterproof Action Camera", "price": "34990", "brand": "GoPro"},
    {"asins": "B08N5WRWNW", "name": "Apple MacBook Air M1 (2020) 256GB", "price": "74990", "brand": "Apple"},
    {"asins": "B0BDHWDR12", "name": "Apple Watch Series 8 [GPS 45mm]", "price": "42999", "brand": "Apple"},
    {"asins": "B0D7MKTK7G", "name": "Dyson Airwrap Multi-Styler Complete Long", "price": "45900", "brand": "Dyson"},
    {"asins": "B0CHWR8EGG", "name": "Apple AirPods Pro (2nd Generation)", "price": "24900", "brand": "Apple"},
]

AUTH_TEXTS = [
    ("Amazing product, totally worth it.", 5),
    ("Pretty good overall, battery life could be better.", 4),
    ("Love the design and performance. Five stars.", 5),
    ("Not bad, but a bit overpriced.", 3),
    ("Excellent purchase. Highly recommend to anyone.", 5),
    ("Decent features, works as expected.", 4),
    ("Average. Nothing extraordinary about it.", 3),
    ("The build quality is superb.", 5),
    ("Sound is crystal clear and fits well.", 4),
    ("A bit heavy but manageable.", 4),
    ("The UI is extremely smooth.", 5),
    ("Expected more from this brand.", 3),
]

FAKE_TEXTS_POS = [
    ("Best product ever! I am so happy wow!", 5),
    ("Perfect perfect perfect! Buy it now!", 5),
    ("I love this so much it changed my life.", 5),
    ("Incredible quality for the price wow.", 5),
    ("Absolutely fantastic! Must have item!!", 5),
    ("10/10 would buy again and again.", 5),
]

FAKE_TEXTS_NEG = [
    ("Terrible do not buy stay away!", 1),
    ("Worst product ever made.", 1),
    ("Complete garbage broke instantly.", 1),
    ("Scam! Do not waste your money.", 1),
    ("Awful experience totally ruined my trip.", 1),
]

USERNAMES = [f"User_{random.randint(1000, 9999)}" for _ in range(200)]

def random_date(start, end):
    return start + timedelta(seconds=random.randint(0, int((end - start).total_seconds())))

def generate_reviews():
    df = pd.read_csv(FILE, low_memory=False)
    new_rows = []
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=365)
    
    for p in PRODUCTS:
        # Determine if this product will be "manipulated" or "authentic"
        is_manipulated = random.choice([True, False])
        total_auth = random.randint(40, 100)
        
        # 1. Authentic baseline
        for _ in range(total_auth):
            txt, rat = random.choice(AUTH_TEXTS)
            dt = random_date(start_date, end_date)
            new_rows.append({
                "asins": p["asins"],
                "name": p["name"],
                "prices": p["price"],
                "brand": p["brand"],
                "reviews.rating": rat,
                "reviews.text": txt,
                "reviews.date": dt.isoformat() + "Z",
                "reviews.username": random.choice(USERNAMES)
            })
            
        if is_manipulated:
            # 2. Add fake burst
            manipulation_type = random.choice(["positive_spike", "negative_attack", "copycat"])
            burst_date = random_date(end_date - timedelta(days=60), end_date - timedelta(days=10))
            burst_size = random.randint(25, 60)
            
            for _ in range(burst_size):
                if manipulation_type == "negative_attack":
                    txt, rat = random.choice(FAKE_TEXTS_NEG)
                elif manipulation_type == "copycat":
                    txt, rat = FAKE_TEXTS_POS[0] # Exact same text repeated
                else:
                    txt, rat = random.choice(FAKE_TEXTS_POS)
                    
                # All clumped in a 3-day window
                dt = burst_date + timedelta(hours=random.randint(1, 72))
                new_rows.append({
                    "asins": p["asins"],
                    "name": p["name"],
                    "prices": p["price"],
                    "brand": p["brand"],
                    "reviews.rating": rat,
                    "reviews.text": txt,
                    "reviews.date": dt.isoformat() + "Z",
                    "reviews.username": f"Bot_{random.randint(100, 999)}"
                })
    
    new_df = pd.DataFrame(new_rows)
    # Give required columns if missing
    for col in df.columns:
        if col not in new_df.columns:
            new_df[col] = ""
            
    combined = pd.concat([df, new_df], ignore_index=True)
    combined.to_csv(FILE, index=False)
    print(f"Added {len(new_rows)} synthesized premium reviews across {len(PRODUCTS)} new products!")

if __name__ == "__main__":
    generate_reviews()
