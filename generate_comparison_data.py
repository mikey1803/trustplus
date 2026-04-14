import json, hashlib, random
from pathlib import Path
import pandas as pd
import numpy as np

SUMMARY = Path("outputs/summary_top_asins.csv")
PRICES_JSON = Path("outputs/price_comparison.json")
REVIEWS_JSON = Path("outputs/fake_reviews.json")

SITES = ["Amazon.in", "Flipkart", "Snapdeal", "Croma", "Reliance Digital"]
SITE_COLORS = {"Amazon.in": "#FF9900", "Flipkart": "#2874F0", "Snapdeal": "#E40046", "Croma": "#00BFA5", "Reliance Digital": "#E31837"}
SITE_URLS = {
    "Amazon.in": "https://www.amazon.in/s?k=",
    "Flipkart": "https://www.flipkart.com/search?q=",
    "Snapdeal": "https://www.snapdeal.com/search?keyword=",
    "Croma": "https://www.croma.com/searchB?q=",
    "Reliance Digital": "https://www.reliancedigital.in/search?q=",
}

REVIEW_TEMPLATES = {
    "positive": [
        "Excellent product! The build quality is amazing and it works flawlessly. Battery life is impressive and the display is crystal clear. Totally worth the investment.",
        "I've been using this for 3 months now and it's still going strong. The performance is top-notch and customer service was very responsive when I had a question.",
        "Great value for money! Compared to competitors, this offers way more features. Setup was easy and the user interface is intuitive.",
        "Perfect gift for tech lovers. My {relation} absolutely loved it. The packaging was premium and delivery was on time.",
        "After extensive research, I chose this over alternatives and I'm so glad I did. The {feature} is particularly impressive.",
        "This exceeded my expectations in every way. The sound quality is rich, the design is sleek, and it pairs seamlessly with my other devices.",
        "Bought this during the sale and it was a steal! Works exactly as advertised. Would definitely recommend to friends and family.",
        "Five stars without hesitation. The {feature} alone makes it worth buying. Plus the 1-year warranty gives peace of mind.",
    ],
    "negative": [
        "Very disappointed. The product stopped working after just 2 weeks. Customer support kept transferring me to different departments.",
        "Not worth the price at all. The {feature} is mediocre at best. Build quality feels cheap and plasticky.",
        "Received a defective unit. The screen had dead pixels and the buttons were unresponsive. Had to initiate a return immediately.",
        "Misleading product description. The actual specs are much lower than advertised. Battery barely lasts {hours} hours.",
        "Terrible experience. The product arrived damaged and the replacement process took 3 weeks. Save your money.",
    ],
    "neutral": [
        "Decent product for the price range. Nothing extraordinary but gets the job done. The {feature} could be better though.",
        "It's okay, not great not terrible. Works as expected most of the time. Sometimes lags a bit during heavy use.",
        "Average quality. I've seen better products in this range but also worse. It serves its purpose for basic needs.",
    ],
}

RELATIONS = ["brother", "sister", "friend", "dad", "mom", "colleague"]
FEATURES = ["battery life", "display quality", "sound system", "processing speed", "camera", "build quality", "connectivity", "storage capacity"]
USERNAMES = [
    "TechGuru_Mumbai", "SmartBuyer_Delhi", "ReviewKing_Bangalore", "GadgetFreak_Chennai",
    "ValueHunter_Hyderabad", "ProductExpert_Pune", "HonestReviewer_Kolkata", "ShopSmart_Jaipur",
    "DigitalNomad_Kochi", "TechSavvy_Ahmedabad", "BudgetBoss_Lucknow", "QualityFirst_Chandigarh",
    "SmartChoice_Indore", "TruthTeller_Nagpur", "WiseBuyer_Bhopal", "RealReview_Surat",
    "TechNerd_Vizag", "HappyShopper_Patna", "CriticalEye_Guwahati", "FairJudge_Ranchi",
]

def _seed(name):
    return int(hashlib.md5(name.encode()).hexdigest()[:8], 16)

def generate_prices(name, base_price):
    """Generate comparison prices from different e-commerce sites."""
    rng = random.Random(_seed(name))
    prices = {}
    for site in SITES:
        # Random variation: -15% to +20% from base
        variation = rng.uniform(0.85, 1.20)
        price = round(base_price * variation, -1)  # Round to nearest 10
        in_stock = rng.random() > 0.15  # 85% chance in stock
        prices[site] = {
            "price": int(price),
            "in_stock": in_stock,
            "url": SITE_URLS[site] + name.replace(" ", "+")[:50],
            "color": SITE_COLORS[site],
        }
    return prices

def generate_reviews(name, trust_score, num_reviews=6):
    """Generate unique fake reviews based on product trust score."""
    rng = random.Random(_seed(name))
    reviews = []

    # Determine review distribution based on trust score
    if trust_score >= 70:
        dist = {"positive": 4, "neutral": 1, "negative": 1}
    elif trust_score >= 40:
        dist = {"positive": 2, "neutral": 2, "negative": 2}
    else:
        dist = {"positive": 1, "neutral": 1, "negative": 4}

    for sentiment, count in dist.items():
        templates = REVIEW_TEMPLATES[sentiment]
        for i in range(min(count, len(templates))):
            template = templates[rng.randint(0, len(templates)-1)]
            text = template.replace("{relation}", rng.choice(RELATIONS))
            text = text.replace("{feature}", rng.choice(FEATURES))
            text = text.replace("{hours}", str(rng.randint(2, 5)))

            rating = {"positive": rng.choice([4, 5, 5, 5]),
                      "neutral": rng.choice([3, 3, 4]),
                      "negative": rng.choice([1, 1, 2])}[sentiment]

            date_offset = rng.randint(1, 180)
            reviews.append({
                "username": rng.choice(USERNAMES),
                "rating": rating,
                "text": text,
                "sentiment": sentiment,
                "date_ago": f"{date_offset} days ago",
                "helpful": rng.randint(0, 25),
                "verified": rng.random() > 0.3,
            })

    rng.shuffle(reviews)
    return reviews[:num_reviews]

def main():
    if not SUMMARY.exists():
        print("❌ No summary. Run pipeline first."); return

    df = pd.read_csv(SUMMARY)
    all_prices = {}
    all_reviews = {}

    for _, row in df.iterrows():
        name = str(row.get("name", row["asins"]))
        try:
            base_price = float(row.get("price_inr", 0))
            if np.isnan(base_price) or base_price <= 0:
                base_price = random.Random(_seed(name)).randint(2000, 15000)
        except (ValueError, TypeError):
            base_price = random.Random(_seed(name)).randint(2000, 15000)
        
        trust = float(row.get("overall_trust", 100))

        all_prices[name] = generate_prices(name, base_price)
        all_reviews[name] = generate_reviews(name, trust)

    PRICES_JSON.write_text(json.dumps(all_prices, indent=2), encoding="utf-8")
    REVIEWS_JSON.write_text(json.dumps(all_reviews, indent=2), encoding="utf-8")
    print(f"✅ Generated prices for {len(all_prices)} products")
    print(f"✅ Generated {sum(len(v) for v in all_reviews.values())} unique reviews")

if __name__ == "__main__":
    main()
