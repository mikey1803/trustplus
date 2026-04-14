import pandas as pd
import json

SUMMARY = "outputs/summary_top_asins.csv"
PRICES = "outputs/price_comparison.json"
REVIEWS = "outputs/fake_reviews.json"

PREMIUM_DATA = {
    "B0CHX2F5QT": ("Apple iPhone 15 Pro Max (256 GB) - Natural Titanium", "https://m.media-amazon.com/images/I/81Os1SDWpcL._SX679_.jpg", 159900),
    "B09XS7JWHH": ("Sony WH-1000XM5 Wireless Noise Canceling Headphones", "https://m.media-amazon.com/images/I/61+btxcsApL._SX522_.jpg", 29990),
    "B0CQPTN5XF": ("Samsung Galaxy S24 Ultra 5G (Titanium Gray, 12GB, 256GB)", "https://m.media-amazon.com/images/I/71CXhVhpM0L._SX679_.jpg", 129999),
    "B0982GYG59": ("Bose Smart Soundbar 900 Dolby Atmos", "https://m.media-amazon.com/images/I/71rQ66B+uDL._SX522_.jpg", 89900),
    "B0CRWBRSBD": ("ASUS ROG Zephyrus G14 Gaming Laptop", "https://m.media-amazon.com/images/I/71jH2tA5+3L._SX679_.jpg", 189990),
    "B0CG7PXYH4": ("GoPro HERO12 Black - Waterproof Action Camera", "https://m.media-amazon.com/images/I/61r5fMUPZ-L._SX522_.jpg", 34990),
    "B08N5WRWNW": ("Apple MacBook Air M1 (2020) 256GB", "https://m.media-amazon.com/images/I/71jG+e7roXL._SX679_.jpg", 74990),
    "B0BDHWDR12": ("Apple Watch Series 8 [GPS 45mm]", "https://m.media-amazon.com/images/I/71XMTLEI0yL._SX679_.jpg", 42999),
    "B0D7MKTK7G": ("Dyson Airwrap Multi-Styler Complete Long", "https://m.media-amazon.com/images/I/51r26tC6I-L._SX522_.jpg", 45900),
    "B0CHWR8EGG": ("Apple AirPods Pro (2nd Generation)", "https://m.media-amazon.com/images/I/61SUj2aKoEL._SX679_.jpg", 24900)
}

SOPHISTICATED_FAKES = [
    "I was skeptical at first, but this absolutely blew my expectations out of the water. Highly recommended!",
    "The build volume and overall finishing is top-notch. I've used similar brands but this one stands out.",
    "Delivery was perfectly on time and packaging was totally secure. Functionally, it does exactly what the OEM claims. 5/5.",
    "A phenomenal investment. It integrates seamlessly into my daily routine without any bugs or hiccups.",
    "Seriously cannot overstate how good the performance is on this model. The battery life exceeds the stated specifications.",
    "Got this on sale and it is a total bargain. Even at full price, it is worth every single penny."
]

SOPHISTICATED_NEGATIVES = [
    "Completely disappointed. The unit arrived with a dead pixel and thermal throttles constantly. Avoid this batch.",
    "Customer service was a nightmare. The firmware update bricked the device within two weeks of light usage.",
    "Overpriced and under-delivers. The battery drains 30% faster than advertised and it feels incredibly cheap."
]

def update_summary():
    df = pd.read_csv(SUMMARY)
    for asin, (name, img, price) in PREMIUM_DATA.items():
        if asin in df['asins'].values:
            df.loc[df['asins'] == asin, 'image_url'] = img
            df.loc[df['asins'] == asin, 'price_inr'] = price
    df.to_csv(SUMMARY, index=False)
    print("CSV Updated!")

def update_prices():
    with open(PRICES, "r") as f:
        data = json.load(f)
        
    import random
    for asin, (name, img, base_price) in PREMIUM_DATA.items():
        if name in data:
            data[name] = {
                "Amazon.in": {"price": base_price, "in_stock": True, "url": f"https://www.amazon.in/dp/{asin}", "color": "#f59e0b"},
                "Flipkart": {"price": int(base_price * random.uniform(0.98, 1.05)), "in_stock": random.choice([True, True, False]), "url": f"https://www.flipkart.com/search?q={name.replace(' ', '+')}", "color": "#3b82f6"},
                "Reliance Digital": {"price": int(base_price * random.uniform(1.0, 1.08)), "in_stock": True, "url": f"https://www.reliancedigital.in/search?q={name.replace(' ', '+')}", "color": "#ef4444"},
                "Croma": {"price": int(base_price * random.uniform(0.99, 1.05)), "in_stock": True, "url": f"https://www.croma.com/search/?q={name.replace(' ', '+')}", "color": "#10b981"},
            }
    with open(PRICES, "w") as f:
        json.dump(data, f, indent=2)
    print("Prices Updated!")

def update_reviews():
    with open(REVIEWS, "r") as f:
        data = json.load(f)
        
    import random
    for name, reviews in data.items():
        for rev in reviews:
            # If it's fake and 5-star, replace with sophisticated text
            if rev['rating'] == 5 and rev['sentiment'] == 'negative':
                rev['text'] = random.choice(SOPHISTICATED_FAKES)
            # If it's fake and 1-star
            elif rev['rating'] <= 2 and rev['sentiment'] == 'positive':
                rev['text'] = random.choice(SOPHISTICATED_NEGATIVES)
                
    with open(REVIEWS, "w") as f:
        json.dump(data, f, indent=2)
    print("Reviews Updated!")

if __name__ == "__main__":
    update_summary()
    update_prices()
    update_reviews()
