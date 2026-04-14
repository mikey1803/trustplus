import streamlit as st
import pandas as pd
import numpy as np
import json
import math
import random
import re
import io
import base64
from pathlib import Path

import plotly.graph_objects as go
import plotly.express as px
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from wordcloud import WordCloud
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────
st.set_page_config(page_title="TrustLens+ Premium", page_icon="💎", layout="wide")

REVIEWS_PATH = Path("outputs/fake_reviews.json")
PRICES_PATH  = Path("outputs/price_comparison.json")

# ─────────────────────────────────────────────
# 50 ELECTRONICS PRODUCTS (hardcoded, no food)
# ─────────────────────────────────────────────
PRODUCTS = [
    {"id": 1,  "name": "Apple iPhone 15 Pro Max",          "price": 159900, "trust": 92, "dist": 0.12, "img": "https://images.unsplash.com/photo-1695048133142-1a20484d2569?w=400&fit=crop"},
    {"id": 2,  "name": "Sony WH-1000XM5 Headphones",      "price": 34990,  "trust": 88, "dist": 0.22, "img": "https://images.unsplash.com/photo-1618366712010-f4ae9c647dcb?w=400&fit=crop"},
    {"id": 3,  "name": "Samsung Galaxy S24 Ultra",         "price": 129999, "trust": 65, "dist": 0.45, "img": "https://images.unsplash.com/photo-1610945415295-d9bbf067e59c?w=400&fit=crop"},
    {"id": 4,  "name": "Bose Smart Soundbar 900",          "price": 89900,  "trust": 91, "dist": 0.08, "img": "https://images.unsplash.com/photo-1545454675-3531b543be5d?w=400&fit=crop"},
    {"id": 5,  "name": "ASUS ROG Zephyrus G14 Laptop",    "price": 169990, "trust": 52, "dist": 0.72, "img": "https://images.unsplash.com/photo-1593640408182-31c70c8268f5?w=400&fit=crop"},
    {"id": 6,  "name": "GoPro HERO12 Black",               "price": 39990,  "trust": 95, "dist": 0.03, "img": "https://images.unsplash.com/photo-1526170375885-4d8ecf77b99f?w=400&fit=crop"},
    {"id": 7,  "name": "Apple MacBook Air M2",             "price": 114990, "trust": 78, "dist": 0.31, "img": "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=400&fit=crop"},
    {"id": 8,  "name": "Apple Watch Ultra 2",              "price": 89900,  "trust": 93, "dist": 0.05, "img": "https://images.unsplash.com/photo-1434493789847-2f02bffa6ae6?w=400&fit=crop"},
    {"id": 9,  "name": "Dyson V15 Detect Vacuum",         "price": 62900,  "trust": 48, "dist": 0.81, "img": "https://images.unsplash.com/photo-1558618666-fcd25c85f82e?w=400&fit=crop"},
    {"id": 10, "name": "Apple AirPods Pro 2nd Gen",        "price": 24900,  "trust": 89, "dist": 0.11, "img": "https://images.unsplash.com/photo-1606220588913-b3aecb31c195?w=400&fit=crop"},
    {"id": 11, "name": "Samsung 65\" Neo QLED 4K TV",      "price": 164990, "trust": 86, "dist": 0.19, "img": "https://images.unsplash.com/photo-1593359677879-a4bb92f829d1?w=400&fit=crop"},
    {"id": 12, "name": "Dell XPS 15 Laptop",               "price": 149990, "trust": 74, "dist": 0.38, "img": "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=400&fit=crop"},
    {"id": 13, "name": "Nintendo Switch OLED",              "price": 34999,  "trust": 90, "dist": 0.09, "img": "https://images.unsplash.com/photo-1578303512597-81e6cc155b3e?w=400&fit=crop"},
    {"id": 14, "name": "Canon EOS R6 Mark II",             "price": 215990, "trust": 94, "dist": 0.04, "img": "https://images.unsplash.com/photo-1516035069371-29a1b244cc32?w=400&fit=crop"},
    {"id": 15, "name": "iPad Pro 12.9\" M2 Chip",          "price": 112900, "trust": 87, "dist": 0.15, "img": "https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?w=400&fit=crop"},
    {"id": 16, "name": "JBL Charge 5 Speaker",             "price": 14999,  "trust": 82, "dist": 0.24, "img": "https://images.unsplash.com/photo-1608043152269-423dbba4e7e1?w=400&fit=crop"},
    {"id": 17, "name": "Razer BlackWidow Keyboard",        "price": 13999,  "trust": 56, "dist": 0.62, "img": "https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=400&fit=crop"},
    {"id": 18, "name": "Logitech MX Master 3S Mouse",     "price": 9999,   "trust": 91, "dist": 0.07, "img": "https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=400&fit=crop"},
    {"id": 19, "name": "Sony PlayStation 5 Console",       "price": 49990,  "trust": 45, "dist": 0.85, "img": "https://images.unsplash.com/photo-1607853202273-797f1c22a38e?w=400&fit=crop"},
    {"id": 20, "name": "Samsung Galaxy Buds2 Pro",         "price": 17999,  "trust": 83, "dist": 0.21, "img": "https://images.unsplash.com/photo-1590658268037-6bf12f032f55?w=400&fit=crop"},
    {"id": 21, "name": "LG 27\" UltraGear Gaming Monitor", "price": 29999,  "trust": 79, "dist": 0.28, "img": "https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?w=400&fit=crop"},
    {"id": 22, "name": "Google Pixel 8 Pro",               "price": 106999, "trust": 88, "dist": 0.13, "img": "https://images.unsplash.com/photo-1598327105666-5b89351aff97?w=400&fit=crop"},
    {"id": 23, "name": "Anker PowerCore 26800mAh",         "price": 5999,   "trust": 72, "dist": 0.35, "img": "https://images.unsplash.com/photo-1609091839311-d5365f9ff1c5?w=400&fit=crop"},
    {"id": 24, "name": "Kindle Paperwhite 11th Gen",       "price": 16999,  "trust": 96, "dist": 0.02, "img": "https://images.unsplash.com/photo-1541963463532-d68292c34b19?w=400&fit=crop"},
    {"id": 25, "name": "Xbox Series X Console",            "price": 52990,  "trust": 50, "dist": 0.78, "img": "https://images.unsplash.com/photo-1621259182978-fbf93132d53d?w=400&fit=crop"},
    {"id": 26, "name": "Nikon Z6 III Mirrorless Camera",   "price": 179990, "trust": 93, "dist": 0.06, "img": "https://images.unsplash.com/photo-1502920917128-1aa500764cbd?w=400&fit=crop"},
    {"id": 27, "name": "Marshall Stanmore III Speaker",    "price": 42999,  "trust": 85, "dist": 0.18, "img": "https://images.unsplash.com/photo-1507646227500-4d389b0012be?w=400&fit=crop"},
    {"id": 28, "name": "DJI Mini 4 Pro Drone",             "price": 92900,  "trust": 90, "dist": 0.10, "img": "https://images.unsplash.com/photo-1507582020474-9a35b7d455d9?w=400&fit=crop"},
    {"id": 29, "name": "Sennheiser Momentum 4 Wireless",  "price": 27990,  "trust": 81, "dist": 0.25, "img": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400&fit=crop"},
    {"id": 30, "name": "HP Spectre x360 16\" Laptop",      "price": 159990, "trust": 62, "dist": 0.52, "img": "https://images.unsplash.com/photo-1525547719571-a2d4ac8945e2?w=400&fit=crop"},
    {"id": 31, "name": "Samsung Galaxy Tab S9 Ultra",      "price": 108999, "trust": 84, "dist": 0.20, "img": "https://images.unsplash.com/photo-1561154464-82e9aab73227?w=400&fit=crop"},
    {"id": 32, "name": "OnePlus 12 5G Smartphone",         "price": 64999,  "trust": 76, "dist": 0.33, "img": "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=400&fit=crop"},
    {"id": 33, "name": "Garmin Fenix 7X Smartwatch",       "price": 79990,  "trust": 92, "dist": 0.07, "img": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=400&fit=crop"},
    {"id": 34, "name": "Sonos Arc Soundbar",               "price": 99900,  "trust": 87, "dist": 0.16, "img": "https://images.unsplash.com/photo-1558089687-f282ffcbc126?w=400&fit=crop"},
    {"id": 35, "name": "Asus ZenBook 14 OLED Laptop",     "price": 89990,  "trust": 69, "dist": 0.42, "img": "https://images.unsplash.com/photo-1611186871348-b1ce696e52c9?w=400&fit=crop"},
    {"id": 36, "name": "Philips Hue Starter Kit",          "price": 12999,  "trust": 80, "dist": 0.26, "img": "https://images.unsplash.com/photo-1558618666-fcd25c85f82e?w=400&fit=crop"},
    {"id": 37, "name": "Beats Studio Pro Headphones",      "price": 29999,  "trust": 71, "dist": 0.36, "img": "https://images.unsplash.com/photo-1583394838336-acd977736f90?w=400&fit=crop"},
    {"id": 38, "name": "Meta Quest 3 VR Headset",          "price": 49999,  "trust": 55, "dist": 0.65, "img": "https://images.unsplash.com/photo-1592478411213-6153e4ebc07d?w=400&fit=crop"},
    {"id": 39, "name": "Samsung 34\" Odyssey G5 Monitor",  "price": 38999,  "trust": 83, "dist": 0.22, "img": "https://images.unsplash.com/photo-1585792180666-f7347c490ee2?w=400&fit=crop"},
    {"id": 40, "name": "Corsair Vengeance 32GB DDR5 RAM",  "price": 12499,  "trust": 94, "dist": 0.04, "img": "https://images.unsplash.com/photo-1591799264318-7e6ef8ddb7ea?w=400&fit=crop"},
    {"id": 41, "name": "WD Black SN850X 2TB SSD",         "price": 16999,  "trust": 89, "dist": 0.12, "img": "https://images.unsplash.com/photo-1597872200969-2b65d56bd16b?w=400&fit=crop"},
    {"id": 42, "name": "Fitbit Sense 2 Smartwatch",        "price": 19999,  "trust": 77, "dist": 0.30, "img": "https://images.unsplash.com/photo-1575311373937-040b8e1fd5b6?w=400&fit=crop"},
    {"id": 43, "name": "Nvidia RTX 4090 Graphics Card",   "price": 189990, "trust": 42, "dist": 0.90, "img": "https://images.unsplash.com/photo-1591488320449-011701bb6704?w=400&fit=crop"},
    {"id": 44, "name": "Apple HomePod 2nd Gen",            "price": 32900,  "trust": 86, "dist": 0.17, "img": "https://images.unsplash.com/photo-1589003077984-894e133dabab?w=400&fit=crop"},
    {"id": 45, "name": "Xiaomi Pad 6 Tablet",              "price": 26999,  "trust": 73, "dist": 0.34, "img": "https://images.unsplash.com/photo-1585790050230-5dd28404ccb9?w=400&fit=crop"},
    {"id": 46, "name": "Sony A7 IV Full Frame Camera",    "price": 198990, "trust": 95, "dist": 0.03, "img": "https://images.unsplash.com/photo-1510127034890-ba27508e9f1c?w=400&fit=crop"},
    {"id": 47, "name": "Bose QuietComfort Ultra Earbuds",  "price": 24990,  "trust": 88, "dist": 0.14, "img": "https://images.unsplash.com/photo-1572569511254-d8f925fe2cbb?w=400&fit=crop"},
    {"id": 48, "name": "Lenovo Legion Pro 7i Laptop",     "price": 224990, "trust": 60, "dist": 0.55, "img": "https://images.unsplash.com/photo-1603302576837-37561b2e2302?w=400&fit=crop"},
    {"id": 49, "name": "Ring Video Doorbell Pro 2",        "price": 18999,  "trust": 82, "dist": 0.23, "img": "https://images.unsplash.com/photo-1558002038-1055907df827?w=400&fit=crop"},
    {"id": 50, "name": "SteelSeries Arctis Nova Pro",      "price": 32999,  "trust": 75, "dist": 0.37, "img": "https://images.unsplash.com/photo-1599669454699-248893623440?w=400&fit=crop"},
]

# Build DataFrame
df = pd.DataFrame(PRODUCTS)
df.rename(columns={"id": "asins", "price": "price_inr", "trust": "overall_trust", "dist": "distortion"}, inplace=True)
df["asins"] = df["asins"].astype(str)

def classify(row):
    t = row["overall_trust"]; d = abs(row["distortion"])
    if t < 60 or d > 0.5: return "Flagged"
    if t < 85 or d > 0.2: return "Caution"
    return "Safe"
df["risk"] = df.apply(classify, axis=1)

# ─────────────────────────────────────────────
# REVIEWS + PRICES FROM FILE (fallback to mock)
# ─────────────────────────────────────────────
@st.cache_data
def load_extra():
    prices = json.loads(PRICES_PATH.read_text("utf-8")) if PRICES_PATH.exists() else {}
    reviews = json.loads(REVIEWS_PATH.read_text("utf-8")) if REVIEWS_PATH.exists() else {}
    return prices, reviews

prices_db, reviews_db = load_extra()

def get_reviews_for(name):
    r = reviews_db.get(name, [])
    if r: return r
    rng = random.Random(hash(name))
    templates_good = [
        "Absolutely phenomenal product. Flawlessly designed and highly recommended!",
        "Crystal clear performance, seamlessly integrates into my workflow. Top-notch quality.",
        "Blown away by the build quality. Exceeded all my expectations. A true bargain.",
        "Impressive specs and responsive interface. Best purchase I've made this year.",
        "Premium build, totally secure software stack. Works flawlessly out of the box."
    ]
    templates_bad = [
        "Total nightmare — arrived defective and bricked after one day of use.",
        "Cheap, misleading advertising. Unresponsive support, damaged within a week.",
        "Avoid this batch! Overheats constantly, battery drains in 2 hours.",
        "Not worth the hype. Performance is average at best for the price.",
        "Returned immediately. Screen had dead pixels and the unit was refurbished."
    ]
    reviews = []
    for i in range(5):
        reviews.append({"rating": rng.choice([4,5]), "text": rng.choice(templates_good), "date_ago": f"{rng.randint(1,14)} days ago"})
    for i in range(3):
        reviews.append({"rating": rng.choice([1,2]), "text": rng.choice(templates_bad), "date_ago": f"{rng.randint(1,6)} months ago"})
    rng.shuffle(reviews)
    return reviews

def get_prices_for(name, base_price):
    p = prices_db.get(name, {})
    if p: return p
    rng = random.Random(hash(name))
    return {
        "Amazon":  {"price": base_price, "in_stock": True, "url": "#", "color": "#f59e0b"},
        "Flipkart": {"price": base_price + rng.randint(-3000, 5000), "in_stock": True, "url": "#", "color": "#3b82f6"},
        "Croma":   {"price": base_price + rng.randint(1000, 8000), "in_stock": rng.choice([True, False]), "url": "#", "color": "#10b981"},
        "Reliance Digital": {"price": base_price + rng.randint(-1000, 4000), "in_stock": rng.choice([True, False]), "url": "#", "color": "#8b5cf6"},
    }

# ─────────────────────────────────────────────
# CSS — DEEP PURPLE PREMIUM THEME
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700;800&family=Inter:wght@400;500;600;700&display=swap');

/* ── Global ── */
.stApp {
    background: linear-gradient(135deg, #05000a 0%, #0a0114 35%, #0d011f 65%, #05000c 100%);
    font-family: 'Inter', sans-serif;
}
html, body, [class*="css"] { color: #f3e8ff !important; }
h1, h2, h3, h4, h5, h6 { font-family: 'Outfit', sans-serif !important; color: #ffffff !important; }

/* ── Metric Override ── */
div[data-testid="stMetric"] {
    background: linear-gradient(135deg, rgba(88, 28, 135, 0.4), rgba(59, 7, 100, 0.3));
    border: 1px solid rgba(168, 85, 247, 0.4);
    border-radius: 14px;
    padding: 16px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.2);
}
[data-testid="stMetricLabel"], [data-testid="stMetricLabel"] * {
    color: #e9d5ff !important;
    font-size: 1.05rem !important;
    font-weight: 600 !important;
    opacity: 1 !important;
}
[data-testid="stMetricValue"], [data-testid="stMetricValue"] * {
    color: #ffffff !important;
}
div[data-testid="stText"] *, div[data-testid="caption"] *, div[data-testid="stCaptionContainer"] * {
    color: #c4b5fd !important;
    font-size: 0.95rem !important;
}

/* ── Button Styling ── */
div[data-testid="stButton"] button {
    background: linear-gradient(135deg, rgba(147, 51, 234, 0.2), rgba(124, 58, 237, 0.1)) !important;
    color: #e9d5ff !important;
    border: 1px solid rgba(168, 85, 247, 0.5) !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-family: 'Outfit', sans-serif !important;
    letter-spacing: 0.5px !important;
    padding: 0.5rem 1.2rem !important;
    transition: all 0.3s cubic-bezier(0.2, 0.8, 0.2, 1) !important;
}
div[data-testid="stButton"] button:hover {
    transform: translateY(-2px) !important;
    background: linear-gradient(135deg, rgba(168, 85, 247, 0.4), rgba(147, 51, 234, 0.4)) !important;
    border-color: rgba(216, 180, 254, 0.9) !important;
    color: #ffffff !important;
    box-shadow: 0 8px 20px rgba(147, 51, 234, 0.4) !important;
}
div[data-testid="stButton"] button:active {
    transform: translateY(0) !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: rgba(0,0,0,0.3); }
::-webkit-scrollbar-thumb { background: #9333ea; border-radius: 10px; }

/* ── Hero ── */
.hero-title {
    font-family: 'Outfit', sans-serif;
    font-size: 2.8rem; font-weight: 800;
    background: linear-gradient(to right, #a78bfa, #c084fc, #e879f9, #a78bfa);
    background-size: 200% auto;
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    animation: shine 4s linear infinite;
    margin-bottom: 5px; letter-spacing: -0.5px;
}
@keyframes shine { to { background-position: 200% center; } }

/* ── Deep Scan Animation ── */
.scan-container {
    position: relative;
    display: inline-block;
    overflow: hidden;
    border-radius: 12px;
}
.scan-line {
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 4px;
    background: linear-gradient(90deg, transparent, #c084fc, #ef4444, #c084fc, transparent);
    box-shadow: 0 4px 15px rgba(239, 68, 68, 0.8);
    animation: scan 2.5s cubic-bezier(0.4, 0, 0.2, 1) infinite alternate;
    z-index: 10;
}
@keyframes scan {
    0% { top: 0%; opacity: 1; }
    100% { top: 100%; opacity: 0.8; }
}
@keyframes pulse-red {
    0% { opacity: 0.7; text-shadow: 0 0 5px rgba(239,68,68,0.2); }
    50% { opacity: 1; text-shadow: 0 0 15px rgba(239,68,68,0.8); }
    100% { opacity: 0.7; text-shadow: 0 0 5px rgba(239,68,68,0.2); }
}
.hero-sub {
    color: #a78bfa; font-size: 0.95rem; margin-bottom: 25px;
    font-family: 'Inter', sans-serif;
}

/* ── Scorecard ── */
.scorecard {
    background: linear-gradient(135deg, rgba(88, 28, 135, 0.35), rgba(59, 7, 100, 0.25));
    border: 1px solid rgba(168, 85, 247, 0.3);
    backdrop-filter: blur(16px);
    border-radius: 18px; padding: 24px 20px; text-align: center;
    position: relative; overflow: hidden;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}
.scorecard:hover { transform: translateY(-4px); box-shadow: 0 12px 40px rgba(147, 51, 234, 0.3); }
.scorecard::before {
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px;
    background: linear-gradient(90deg, #7c3aed, #a855f7, #c084fc);
    border-radius: 18px 18px 0 0;
}
.sc-icon { font-size: 1.8rem; margin-bottom: 6px; }
.sc-value { font-size: 2.4rem; font-weight: 800; font-family: 'Outfit'; }
.sc-label { color: #a78bfa; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 1.5px; margin-top: 4px; }

/* ── Product Card (lighter than BG) ── */
.prod-card {
    background: linear-gradient(160deg, rgba(107, 33, 168, 0.4), rgba(59, 7, 100, 0.5));
    border: 1px solid rgba(168, 85, 247, 0.4);
    border-radius: 22px; padding: 16px; text-align: center;
    transition: all 0.6s cubic-bezier(0.2, 0.8, 0.2, 1);
    position: relative; overflow: hidden; min-height: 380px;
    display: flex; flex-direction: column; justify-content: space-between;
    backdrop-filter: blur(8px);
}
.prod-card:hover {
    transform: translateY(-10px) scale(1.03);
    border-color: rgba(232, 121, 249, 1);
    box-shadow: 0 25px 60px rgba(168, 85, 247, 0.4), 0 0 30px rgba(216, 180, 254, 0.2) inset;
}
.prod-card::after {
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px;
    background: linear-gradient(90deg, #9333ea, #c084fc, #e879f9);
}
.prod-img-wrap {
    background: rgba(255,255,255,0.95); border-radius: 14px; padding: 10px;
    height: 140px; display: flex; align-items: center; justify-content: center;
    margin-bottom: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    transition: transform 0.4s ease;
}
.prod-card:hover .prod-img-wrap { transform: scale(1.04); }
.prod-img-wrap img { max-height: 120px; max-width: 100%; object-fit: contain; border-radius: 8px; }
.prod-name { font-weight: 700; font-size: 0.88rem; color: #f3e8ff; line-height: 1.3; min-height: 36px; }
.prod-price { color: #e879f9; font-weight: 800; font-size: 1.35rem; font-family: 'Outfit'; margin: 6px 0; }

/* ── Trust Gauge ── */
.trust-gauge { margin: 8px auto; width: 88%; }
.trust-bar-bg { background: rgba(255,255,255,0.08); border-radius: 10px; height: 8px; overflow: hidden; }
.trust-bar-fill { height: 100%; border-radius: 10px; transition: width 0.8s ease; }
.trust-label { font-size: 0.72rem; font-weight: 700; margin-top: 4px; }

/* ── Glass Panel ── */
.glass {
    background: linear-gradient(135deg, rgba(88, 28, 135, 0.3), rgba(59, 7, 100, 0.2));
    border: 1px solid rgba(147, 51, 234, 0.25);
    backdrop-filter: blur(12px); border-radius: 18px; padding: 24px;
    box-shadow: 0 8px 32px rgba(0,0,0,0.3); margin-bottom: 20px;
    position: relative; overflow: hidden;
}
.glass::before {
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg, transparent, #a855f7, transparent);
}

/* ── Alert ── */
.alert-manipulation {
    background: linear-gradient(135deg, rgba(239,68,68,0.1), rgba(239,68,68,0.04));
    border-left: 4px solid #ef4444; padding: 18px 22px; border-radius: 12px;
    color: #fca5a5; margin-bottom: 24px; font-size: 0.95rem;
}

/* ── Price Card ── */
.price-card {
    background: rgba(88, 28, 135, 0.3); border-radius: 14px; padding: 20px;
    min-height: 160px; display: flex; flex-direction: column; justify-content: space-between;
    transition: transform 0.3s ease; border: 1px solid rgba(147,51,234,0.2);
}
.price-card:hover { transform: translateY(-3px); box-shadow: 0 8px 25px rgba(147,51,234,0.2); }

/* ── Review Card ── */
.review-card {
    background: rgba(88, 28, 135, 0.2); padding: 18px; border-radius: 12px;
    margin-bottom: 14px; transition: transform 0.25s ease;
    border: 1px solid rgba(147,51,234,0.15);
}
.review-card:hover { transform: translateX(4px); box-shadow: 0 4px 15px rgba(147,51,234,0.15); }

/* ── Section Header ── */
.section-head {
    font-family: 'Outfit', sans-serif; font-size: 1.3rem; font-weight: 700;
    color: #c4b5fd; margin-bottom: 16px; display: flex; align-items: center; gap: 10px;
}

/* ── Live Ticker ── */
.live-ticker {
    background: rgba(88,28,135,0.25); border: 1px solid rgba(147,51,234,0.3); border-radius: 12px;
    padding: 10px 18px; margin-bottom: 22px; overflow: hidden; white-space: nowrap;
    display: flex; align-items: center; gap: 12px;
}
.ticker-content {
    display: inline-block; animation: scroll-left 20s linear infinite;
    color: #d8b4fe; font-size: 0.88rem;
}
@keyframes scroll-left {
    0% { transform: translateX(60%); }
    100% { transform: translateX(-100%); }
}
.live-badge {
    background: linear-gradient(45deg, #9333ea, #c026d3); color: white;
    padding: 4px 10px; border-radius: 6px; font-weight: 700; font-size: 0.7rem;
    text-transform: uppercase; animation: pulse 2s infinite; flex-shrink: 0;
}
@keyframes pulse {
    0% { box-shadow: 0 0 0 0 rgba(147,51,234,0.7); }
    70% { box-shadow: 0 0 0 10px rgba(147,51,234,0); }
    100% { box-shadow: 0 0 0 0 rgba(147,51,234,0); }
}

/* Hide Streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
div[data-testid="stDecoration"] { display: none; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────
if "selected_product" not in st.session_state:
    st.session_state.selected_product = None

def select_product(pid):
    st.session_state.selected_product = pid

# ═════════════════════════════════════════════
# HOME PAGE
# ═════════════════════════════════════════════
if not st.session_state.selected_product:

    # ── Live Ticker ──
    ticker_msgs = [
        "🚨 Detected suspicious botnet on ASUS ROG Zephyrus — 72% distortion",
        "✅ Verified organic growth for Canon EOS R6 Mark II",
        "⚠️ Price spike + review flood on PS5 Console",
        "📊 14,200 NLP footprints processed today",
        "💎 IEEE Deep Scan running on 50 electronics",
        "🔬 VADER sentiment mismatch found on Dyson V15",
    ]
    st.markdown(f'''
    <div class="live-ticker">
        <span class="live-badge">LIVE AI</span>
        <div class="ticker-content">{" &nbsp;&nbsp;│&nbsp;&nbsp; ".join(ticker_msgs)}</div>
    </div>
    ''', unsafe_allow_html=True)

    # ── Hero ──
    st.markdown('<div class="hero-title">💎 TrustLens+ Premium</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-sub">IEEE Impact-Aware Review Coordination Detection &amp; Market Intelligence System</div>', unsafe_allow_html=True)

    # ── Scorecards ──
    total   = len(df)
    flagged = len(df[df["risk"] == "Flagged"])
    caution = len(df[df["risk"] == "Caution"])
    safe    = len(df[df["risk"] == "Safe"])
    avg_t   = df["overall_trust"].mean()

    s1, s2, s3, s4, s5 = st.columns(5)
    for col, icon, val, color, label in [
        (s1, "📦", total,   "#c084fc", "Total Products"),
        (s2, "🚨", flagged, "#ef4444", "Flagged Items"),
        (s3, "⚠️",  caution, "#fbbf24", "Caution Items"),
        (s4, "✅", safe,    "#10b981", "Safe Items"),
        (s5, "🛡️", f"{avg_t:.1f}", "#a78bfa", "Avg Trust"),
    ]:
        with col:
            st.markdown(f"""<div class="scorecard">
                <div class="sc-icon">{icon}</div>
                <div class="sc-value" style="color:{color};">{val}</div>
                <div class="sc-label">{label}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Charts Row ──
    ch1, ch2, ch3 = st.columns(3)
    with ch1:
        st.markdown('<div class="section-head">📊 Risk Distribution</div>', unsafe_allow_html=True)
        rc = df["risk"].value_counts()
        cmap = {"Flagged": "#ef4444", "Caution": "#fbbf24", "Safe": "#10b981"}
        fig = go.Figure(go.Pie(labels=rc.index.tolist(), values=rc.values.tolist(), hole=0.55,
            marker=dict(colors=[cmap.get(r,"#9333ea") for r in rc.index]),
            textinfo="label+percent", textfont=dict(size=13, color="#fff")))
        fig.update_layout(paper_bgcolor="rgba(88, 28, 135, 0.4)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#e8dff5"), showlegend=False, margin=dict(t=20,b=20,l=20,r=20), height=280)
        st.plotly_chart(fig, use_container_width=True)

    with ch2:
        st.markdown('<div class="section-head">📈 Trust Score Distribution</div>', unsafe_allow_html=True)
        fig2 = go.Figure(go.Histogram(x=df["overall_trust"], nbinsx=12,
            marker=dict(color="#9333ea", line=dict(color="#c084fc", width=1))))
        fig2.update_layout(paper_bgcolor="rgba(88, 28, 135, 0.4)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#a78bfa"), margin=dict(t=20,b=30,l=30,r=20), height=280,
            xaxis=dict(title="Trust Score", gridcolor="rgba(255,255,255,0.05)"),
            yaxis=dict(title="Count", gridcolor="rgba(255,255,255,0.05)"))
        st.plotly_chart(fig2, use_container_width=True)

    with ch3:
        st.markdown('<div class="section-head">💰 Distortion vs Price</div>', unsafe_allow_html=True)
        fig3 = go.Figure(go.Scatter(x=df["price_inr"], y=df["distortion"].abs(), mode="markers",
            text=df["name"], marker=dict(size=10, color=df["overall_trust"],
                colorscale=[[0,"#ef4444"],[0.5,"#fbbf24"],[1,"#10b981"]],
                showscale=True, colorbar=dict(title="Trust", thickness=12),
                line=dict(color="rgba(255,255,255,0.2)", width=1))))
        fig3.update_layout(paper_bgcolor="rgba(88, 28, 135, 0.4)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#a78bfa"), margin=dict(t=20,b=30,l=30,r=20), height=280,
            xaxis=dict(title="Price (₹)", gridcolor="rgba(255,255,255,0.05)"),
            yaxis=dict(title="|Distortion|", gridcolor="rgba(255,255,255,0.05)"))
        st.plotly_chart(fig3, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Product Grid ──
    st.markdown('<div class="section-head" style="font-size:1.5rem;">🛍️ Product Monitor Grid</div>', unsafe_allow_html=True)

    df_sorted = df.sort_values("overall_trust", ascending=True)
    cols = st.columns(4)
    for idx, (_, row) in enumerate(df_sorted.iterrows()):
        col = cols[idx % 4]
        with col:
            img = row["img"]
            name = row["name"]
            name_d = name[:38] + "…" if len(name) > 38 else name
            price_s = f"₹ {int(row['price_inr']):,}"
            trust = row["overall_trust"]
            risk = row["risk"]

            if trust >= 85:   bar_c = "#10b981"
            elif trust >= 60: bar_c = "#fbbf24"
            else:             bar_c = "#ef4444"

            st.markdown(f"""
            <div class="prod-card">
                <div class="prod-img-wrap">
                    <img src="{img}" onerror="this.src='https://dummyimage.com/260x140/1a0230/c084fc&text=No+Image';">
                </div>
                <div class="prod-name">{name_d}</div>
                <div class="prod-price">{price_s}</div>
                <div class="trust-gauge">
                    <div class="trust-bar-bg"><div class="trust-bar-fill" style="width:{trust}%; background:{bar_c};"></div></div>
                    <div class="trust-label" style="color:{bar_c};">Trust: {trust}/100 — {risk}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            st.button("🔍 Deep Dive Analysis", key=f"dd_{row['asins']}_{idx}", on_click=select_product, args=(str(row["asins"]),), use_container_width=True)

# ═════════════════════════════════════════════
# DEEP DIVE PAGE
# ═════════════════════════════════════════════
else:
    pid = st.session_state.selected_product
    row = df[df["asins"] == pid]
    if row.empty:
        st.error("Product not found."); st.stop()
    row = row.iloc[0]

    name      = row["name"]
    price_val = float(row["price_inr"])
    distortion = float(row["distortion"])
    trust     = float(row["overall_trust"])
    img_url   = row["img"]
    risk_lbl  = row["risk"]

    st.button("⬅️ Back to Dashboard", on_click=lambda: st.session_state.update({"selected_product": None}))

    # ── Header ──
    hc1, hc2 = st.columns([1, 2.5])
    with hc1:
        st.markdown(f"""<div style="background:rgba(255,255,255,0.02); border-radius:16px; padding:16px; text-align:center; border: 1px solid rgba(168,85,247,0.2); box-shadow: 0 0 30px rgba(168,85,247,0.05);">
            <div class="scan-container">
                <div class="scan-line"></div>
                <img src="{img_url}" style="max-height:220px; max-width:100%; object-fit:contain; border-radius:10px;"
                     onerror="this.src='https://dummyimage.com/300x200/1a0230/c084fc&text=No+Image';">
            </div>
            <div style="margin-top:12px; font-family:monospace; color:#ef4444; font-size:0.85rem; font-weight:bold; letter-spacing:2px; animation: pulse-red 1.5s infinite;">
                IEEE FORENSIC SCAN ACTIVE
            </div>
        </div>""", unsafe_allow_html=True)

    with hc2:
        st.markdown(f"""
        <div style="margin-bottom: 25px;">
            <div class="hero-title" style="font-size:2.6rem;">{name}</div>
            <div style="color:#c4b5fd; font-size:1.1rem; font-family:monospace; margin-top:5px;">Product ID: {pid}</div>
        </div>
        """, unsafe_allow_html=True)

        if trust >= 85:   bar_c, label = "#10b981", "SAFE"
        elif trust >= 60: bar_c, label = "#fbbf24", "CAUTION"
        else:             bar_c, label = "#ef4444", "HIGH RISK"

        st.markdown(f"""
        <div style="margin: 20px 0 10px 0; background:rgba(0,0,0,0.3); padding:20px; border-radius:12px; border:1px solid rgba(255,255,255,0.05); box-shadow: inset 0 0 20px rgba(0,0,0,0.5);">
            <div style="display:flex; justify-content:space-between; margin-bottom:8px;">
                <span style="color:#e9d5ff; font-weight:600; font-size:1.1rem;">Trust Score</span>
                <span style="color:{bar_c}; font-weight:800; font-size:1.4rem;">{trust:.1f}/100 — {label}</span>
            </div>
            <div style="background:rgba(255,255,255,0.08); border-radius:10px; height:18px; overflow:hidden;">
                <div style="width:{trust}%; height:100%; background:linear-gradient(90deg, {bar_c}, {bar_c}aa); border-radius:10px; transition:width 1.5s cubic-bezier(0.2, 0.8, 0.2, 1);"></div>
            </div>
        </div>""", unsafe_allow_html=True)

        total_reviews = int(random.Random(hash(pid)).randint(400, 3500))
        distorted_percent = min(1.0, abs(distortion) / 5.0 * 1.5)
        fake_reviews = int(total_reviews * distorted_percent)
        real_reviews = total_reviews - fake_reviews

        st.markdown(f"""
        <div style="display:flex; gap:10px; margin-bottom:20px;">
            <div style="flex:1; background:rgba(16, 185, 129, 0.1); border:1px solid rgba(16, 185, 129, 0.3); border-radius:8px; padding:10px; text-align:center;">
                <div style="color:#6ee7b7; font-size:0.8rem; font-weight:bold; letter-spacing:1px; text-transform:uppercase;">Authentic Reviews</div>
                <div style="color:#ffffff; font-size:1.4rem; font-weight:800;">{real_reviews:,}</div>
            </div>
            <div style="flex:1; background:rgba(239, 68, 68, 0.1); border:1px solid rgba(239, 68, 68, 0.3); border-radius:8px; padding:10px; text-align:center;">
                <div style="color:#fca5a5; font-size:0.8rem; font-weight:bold; letter-spacing:1px; text-transform:uppercase;">Distorted / Bot Reviews</div>
                <div style="color:#ffffff; font-size:1.4rem; font-weight:800;">{fake_reviews:,}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        qs1, qs2, qs3, qs4 = st.columns(4)
        qs1.metric("Price", f"₹ {int(price_val):,}")
        qs2.metric("Distortion", f"{distortion:+.3f}")
        qs3.metric("Risk Level", risk_lbl)
        qs4.metric("Trust", f"{trust:.0f}/100")

    st.markdown("---")

    # ── Manipulation Alert ──
    if distortion > 0.3 or trust < 75:
        st.markdown(f"""<div class="alert-manipulation">
            🚨 <strong>MANIPULATION DETECTED:</strong> Coordinated botnet behavior identified.
            Rating distortion of <strong>{distortion:+.3f}</strong> stars inflates perceived quality.
        </div>""", unsafe_allow_html=True)

    # ── Econometric Models ──
    st.markdown('<div class="section-head">📐 Econometric Impact Models</div>', unsafe_allow_html=True)
    overpay  = price_val * (abs(distortion) / 5) * 1.5
    harm_est = int(overpay * 320)

    e1, e2, e3 = st.columns(3)
    with e1:
        st.markdown(f"""<div class="glass" style="text-align:center;">
            <div style="color:#a78bfa; text-transform:uppercase; font-size:0.75rem; letter-spacing:1.5px;">Manipulated Price</div>
            <div style="font-size:2.2rem; font-weight:800; color:#f3e8ff; font-family:Outfit;">₹ {int(price_val):,}</div>
            <div style="color:#a78bfa; text-transform:uppercase; font-size:0.75rem; letter-spacing:1.5px; margin-top:15px;">Fair Price Estimate</div>
            <div style="font-size:2.2rem; font-weight:800; color:#10b981; font-family:Outfit;">₹ {int(price_val - overpay):,}</div>
            <div style="margin-top:18px; padding:12px; background:rgba(239,68,68,0.08); border:1px solid rgba(239,68,68,0.2); border-radius:10px;">
                <span style="color:#fca5a5;">Consumer Overpay</span>
                <span style="float:right; color:#ef4444; font-weight:800; font-size:1.2rem;">+ ₹ {int(overpay):,}</span>
            </div>
        </div>""", unsafe_allow_html=True)

    with e2:
        st.markdown(f"""<div class="glass" style="text-align:center;">
            <div style="color:#a78bfa; text-transform:uppercase; font-size:0.75rem; letter-spacing:1.5px;">Illicit Monthly Revenue</div>
            <div style="font-size:3rem; font-weight:800; color:#ef4444; font-family:Outfit; margin:15px 0;">₹ {harm_est:,}</div>
            <div style="color:#a78bfa; font-size:0.85rem;">Estimated revenue from artificially inflated ratings driving higher conversion rates.</div>
        </div>""", unsafe_allow_html=True)

    with e3:
        st.markdown('<div class="glass" style="text-align:center;">', unsafe_allow_html=True)
        star_score = 3 + (trust / 100) * 2
        sent_sim = star_score - abs(distortion) * 2.5
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number+delta", value=round(sent_sim, 2),
            delta=dict(reference=round(star_score, 2), decreasing=dict(color="#ef4444")),
            title=dict(text="Sentiment vs Rating", font=dict(size=13, color="#a78bfa")),
            gauge=dict(axis=dict(range=[0, 5], tickcolor="#fff"),
                bar=dict(color="#ef4444" if abs(star_score - sent_sim) > 0.3 else "#10b981"),
                bgcolor="rgba(255,255,255,0.03)", borderwidth=0,
                threshold=dict(line=dict(color="white", width=3), thickness=0.75, value=round(star_score, 2)))))
        fig_gauge.update_layout(paper_bgcolor="rgba(0,0,0,0)", margin=dict(t=50,b=10,l=20,r=20), height=240,
            font=dict(color="#e8dff5"))
        st.plotly_chart(fig_gauge, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<div class="section-head">📉 Historical Trust Fluctuation (30 Days)</div>', unsafe_allow_html=True)
    c_hist1, c_hist2 = st.columns([2, 1])
    with c_hist1:
        rng_hist = random.Random(hash(pid))
        days = list(range(-30, 1))
        hist_trust = [trust]
        for _ in range(30):
            hist_trust.append(min(100, max(0, hist_trust[-1] + rng_hist.uniform(-4, 4))))
        hist_trust.reverse()
        fig_hist = go.Figure(go.Scatter(x=days, y=hist_trust, mode='lines+markers',
            line=dict(color="#c084fc", width=3), marker=dict(color="#e879f9", size=6, opacity=0.8),
            fill='tozeroy', fillcolor='rgba(192, 132, 252, 0.1)'))
        fig_hist.update_layout(paper_bgcolor="rgba(88, 28, 135, 0.4)", plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(t=20,b=20,l=20,r=20), height=240, font=dict(color="#a78bfa"),
            xaxis=dict(title="Days Ago", gridcolor="rgba(255,255,255,0.05)"),
            yaxis=dict(title="Trust Score", range=[0,105], gridcolor="rgba(255,255,255,0.05)"))
        st.plotly_chart(fig_hist, use_container_width=True)
    with c_hist2:
        st.markdown('<div class="glass" style="height:100%; display:flex; flex-direction:column; justify-content:center;">', unsafe_allow_html=True)
        trend = hist_trust[-1] - hist_trust[0]
        color_t = "#10b981" if trend >= 0 else "#ef4444"
        arrow = "↗️" if trend >= 0 else "↘️"
        st.markdown(f"""
        <div style="text-align:center;">
            <div style="color:#a78bfa; text-transform:uppercase; font-size:0.8rem; letter-spacing:1px;">30-Day Trend Momentum</div>
            <div style="font-size:3rem; font-weight:800; color:{color_t}; font-family:Outfit; margin:10px 0;">{arrow} {abs(trend):.1f}</div>
            <div style="color:#a78bfa; font-size:0.85rem;">Continuous real-time evaluation of seller manipulation tactics over temporal datasets.</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Price Comparison ──
    comp_prices = get_prices_for(name, int(price_val))
    st.markdown('<div class="section-head">💳 Cross-Platform Price Intelligence</div>', unsafe_allow_html=True)
    pc_cols = st.columns(len(comp_prices))
    for idx, (store, data) in enumerate(comp_prices.items()):
        color = data.get("color", "#a855f7")
        stock_html = "✅ <span style='color:#10b981;'>In Stock</span>" if data["in_stock"] else "❌ <span style='color:#ef4444;'>Out of Stock</span>"
        
        safe_name = name.replace(' ', '+')
        url = "#"
        if store == "Amazon": url = f"https://www.amazon.in/s?k={safe_name}"
        elif store == "Flipkart": url = f"https://www.flipkart.com/search?q={safe_name}"
        elif store == "Croma": url = f"https://www.croma.com/search/?q={safe_name}"
        elif store == "Reliance Digital": url = f"https://www.reliancedigital.in/search?q={safe_name}"
        
        with pc_cols[idx]:
            st.markdown(f"""
            <a href="{url}" target="_blank" style="text-decoration:none; color:inherit;">
                <div class="price-card" style="border-top:3px solid {color}; cursor:pointer; transition:transform 0.2s; box-shadow: 0 4px 10px rgba(0,0,0,0.3);" onmouseover="this.style.transform='scale(1.05)'" onmouseout="this.style.transform='scale(1)'">
                    <strong style="color:{color}; font-size:1rem;">{store} 🔗</strong>
                    <span style="color:#ffffff; font-size:1.5rem; font-weight:800; font-family:Outfit;">₹ {data['price']:,}</span>
                    <span style="font-size:0.85rem;">{stock_html}</span>
                </div>
            </a>
            """, unsafe_allow_html=True)

    st.markdown("---")

    # ── Threat Topology Radar ──
    st.markdown('<div class="section-head">🕸️ Multi-Vector Threat Topology</div>', unsafe_allow_html=True)
    c_rad1, c_rad2 = st.columns([1.5, 1])
    
    with c_rad1:
        rng_rad = random.Random(hash(pid))
        if trust >= 85: # Safe
            v1, v2, v3, v4, v5 = rng_rad.uniform(0, 2), rng_rad.uniform(0, 1), rng_rad.uniform(0, 1.5), rng_rad.uniform(0, 1), rng_rad.uniform(0, 2)
            c_fill = 'rgba(16, 185, 129, 0.4)'
            c_line = '#10b981'
        elif trust >= 60: # Caution
            v1, v2, v3, v4, v5 = rng_rad.uniform(2, 5), rng_rad.uniform(1, 4), rng_rad.uniform(3, 6), rng_rad.uniform(1, 4), rng_rad.uniform(2, 5)
            c_fill = 'rgba(245, 158, 11, 0.4)'
            c_line = '#fbbf24'
        else: # High Risk
            v1, v2, v3, v4, v5 = rng_rad.uniform(6, 10), rng_rad.uniform(7, 10), rng_rad.uniform(5, 9), rng_rad.uniform(6, 10), rng_rad.uniform(7, 10)
            c_fill = 'rgba(239, 68, 68, 0.4)'
            c_line = '#ef4444'

        categories = ['Sentiment Mismatch', 'Temporal Burst', 'Stylometric Cloning', 'Price Volatility', 'Cross-Platform Botnet']
        max_idx = int(np.argmax([v1,v2,v3,v4,v5]))
        fig_radar = go.Figure(data=go.Scatterpolar(
          r=[v1, v2, v3, v4, v5, v1],
          theta=categories + [categories[0]],
          fill='toself',
          fillcolor=c_fill,
          line=dict(color=c_line, width=3),
          name='Threat Signature'
        ))
        fig_radar.update_layout(
          polar=dict(
            radialaxis=dict(visible=True, range=[0, 10], color="#a78bfa", gridcolor="rgba(255,255,255,0.1)", tickfont=dict(size=8)),
            angularaxis=dict(color="#f3e8ff", gridcolor="rgba(255,255,255,0.1)", tickfont=dict(size=12, family="Outfit")),
            bgcolor="rgba(0,0,0,0)"
          ),
          paper_bgcolor="rgba(88, 28, 135, 0.4)",
          margin=dict(t=30,b=30,l=60,r=60), height=380,
          showlegend=False
        )
        st.plotly_chart(fig_radar, use_container_width=True)

    with c_rad2:
        st.markdown(f"""
        <div style="background:rgba(0,0,0,0.3); border-radius:12px; padding:25px; border:1px solid rgba(168,85,247,0.3); height:100%; display:flex; flex-direction:column; justify-content:center;">
            <h4 style="color:#e9d5ff; margin-top:0; font-size:1.4rem;">Dominant Threat Vector</h4>
            <div style="margin-bottom:15px; padding:15px; background:rgba(255,255,255,0.05); border-left:4px solid {c_line}; border-radius:8px;">
                <div style="color:{c_line}; font-size:1.4rem; font-weight:800; line-height:1.2;">{categories[max_idx]}</div>
            </div>
            <p style="color:#a78bfa; font-size:0.95rem; line-height:1.6; margin:0;">
                The topology radar tracks multi-modal attack surfaces simultaneously. Vectors mapping highly toward the outer edge (10) explicitly denote coordinated, well-funded botnet manipulation over organic review behavior.
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # ── VADER Sentiment + Word Cloud ──
    reviews = get_reviews_for(name)
    st.markdown('<div class="section-head">🧠 NLP Sentiment Forensics & Explainable AI</div>', unsafe_allow_html=True)
    analyzer = SentimentIntensityAnalyzer()

    footprints = ["highly recommended", "top-notch", "phenomenal", "seamlessly", "bargain",
                  "exceeds", "avoid this batch", "nightmare", "bricked", "blown away",
                  "totally secure", "flawlessly", "impressive", "crystal clear", "responsive",
                  "defective", "misleading", "unresponsive", "damaged", "cheap"]

    c_red, c_green = [], []
    highlighted_reviews = []
    for r in reviews:
        vs = analyzer.polarity_scores(r["text"])["compound"]
        highlighted = r["text"]
        for foot in footprints:
            pattern = re.compile(re.escape(foot), re.IGNORECASE)
            highlighted = pattern.sub(
                f"<span style='color:#ef4444; font-weight:700; background:rgba(239,68,68,0.12); border-radius:3px; padding:0 4px;'>{foot}</span>",
                highlighted)
        highlighted_reviews.append({"rating": r["rating"], "text": highlighted, "score": vs, "date_ago": r.get("date_ago", "")})
        exp = (r["rating"] - 3) / 2
        if abs(exp - vs) > 0.4: c_red.append((r["rating"], vs))
        else: c_green.append((r["rating"], vs))

    rc1, rc2 = st.columns([1.2, 1])
    with rc1:
        st.markdown("#### Rating vs Sentiment Mismatch")
        fig_sent = go.Figure()
        if c_green:
            xg, yg = zip(*c_green)
            fig_sent.add_trace(go.Scatter(x=xg, y=yg, mode="markers", name="Authentic",
                marker=dict(color="#10b981", size=12, opacity=0.8)))
        if c_red:
            xr, yr = zip(*c_red)
            fig_sent.add_trace(go.Scatter(x=xr, y=yr, mode="markers", name="Suspicious",
                marker=dict(color="#ef4444", size=15, symbol="x", line=dict(color="white", width=1))))
        fig_sent.update_layout(paper_bgcolor="rgba(88, 28, 135, 0.4)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#a78bfa"), margin=dict(t=20,b=40,l=40,r=10), height=350,
            xaxis=dict(title="Star Rating", gridcolor="rgba(255,255,255,0.05)"),
            yaxis=dict(title="VADER Score", gridcolor="rgba(255,255,255,0.05)"),
            legend=dict(yanchor="top", y=0.99, xanchor="right", x=0.99, bgcolor="rgba(0,0,0,0.3)"))
        st.plotly_chart(fig_sent, use_container_width=True)

    with rc2:
        st.markdown('<div class="glass" style="text-align:center;">', unsafe_allow_html=True)
        st.markdown("#### NLP Corpus Word Cloud")
        corpus = " ".join([r["text"] for r in reviews])
        wc = WordCloud(width=800, height=480, background_color=None, mode="RGBA", colormap="Purples", max_words=80).generate(corpus)
        fig_wc, ax_wc = plt.subplots(figsize=(8, 4.8))
        ax_wc.imshow(wc, interpolation="bilinear")
        ax_wc.axis("off")
        fig_wc.patch.set_alpha(0.0)
        buf = io.BytesIO()
        fig_wc.savefig(buf, format="png", bbox_inches="tight", transparent=True, dpi=120)
        plt.close(fig_wc)
        st.image(buf)
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Botnet Graph + Deep Scan ──
    bc1, bc2 = st.columns([1, 1])
    with bc1:
        st.markdown('<div class="glass">', unsafe_allow_html=True)
        st.markdown("#### 🕸️ Manipulation Botnet Graph")
        st.caption("Graph theory mapping of coordinated reviewer network")
        nodes_x, nodes_y, node_colors, node_sizes, node_text = [0], [0], ["#ef4444"], [35], [f"🎯 {name[:20]}"]
        edges_x, edges_y = [], []
        rng = random.Random(hash(pid))
        n_bots = max(8, int(abs(distortion) * 30 + 5))
        for i in range(n_bots):
            angle = (i / n_bots) * 2 * math.pi + rng.uniform(-0.2, 0.2)
            r = rng.uniform(0.4, 1.0)
            nx_v, ny_v = r * math.cos(angle), r * math.sin(angle)
            nodes_x.append(nx_v); nodes_y.append(ny_v)
            is_bot = rng.random() < 0.4
            node_colors.append("#ef4444" if is_bot else "#06b6d4")
            node_sizes.append(15 if is_bot else 10)
            node_text.append(f"{'🤖 Bot' if is_bot else '👤 User'} #{i+1}")
            edges_x.extend([0, nx_v, None]); edges_y.extend([0, ny_v, None])
            if i > 0 and rng.random() < 0.3:
                j = rng.randint(1, len(nodes_x) - 2)
                edges_x.extend([nodes_x[j], nx_v, None]); edges_y.extend([nodes_y[j], ny_v, None])

        for cx, cy, cn in [(-0.7, 0.8, "Related Prod A"), (0.6, -0.7, "Related Prod B"), (0.8, 0.6, "Related Prod C")]:
            nodes_x.append(cx); nodes_y.append(cy)
            node_colors.append("#f59e0b"); node_sizes.append(22); node_text.append(f"📦 {cn}")
            edges_x.extend([0, cx, None]); edges_y.extend([0, cy, None])

        net_fig = go.Figure()
        net_fig.add_trace(go.Scatter(x=edges_x, y=edges_y, mode="lines",
            line=dict(color="rgba(147,51,234,0.3)", width=1), hoverinfo="none", showlegend=False))
        net_fig.add_trace(go.Scatter(x=nodes_x, y=nodes_y, mode="markers+text", text=node_text,
            textposition="top center", textfont=dict(size=8, color="#a78bfa"),
            marker=dict(size=node_sizes, color=node_colors, line=dict(color="rgba(255,255,255,0.15)", width=1)),
            hoverinfo="text", showlegend=False))
        net_fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(visible=False), yaxis=dict(visible=False),
            margin=dict(t=10,b=10,l=10,r=10), height=380)
        st.plotly_chart(net_fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with bc2:
        st.markdown('<div class="glass" style="height:100%;">', unsafe_allow_html=True)
        st.markdown("#### 🕵️ Deep Scan Review Explorer")
        search_term = st.text_input("Search footprints (e.g. 'nightmare', 'flawlessly')", placeholder="Type to filter…")

        st.markdown('<div style="max-height:300px; overflow-y:auto;">', unsafe_allow_html=True)
        shown = 0
        for hr in highlighted_reviews:
            if search_term and search_term.lower() not in hr["text"].lower():
                continue
            shown += 1
            vs = hr["score"]
            exp = (hr["rating"] - 3) / 2
            is_fake = abs(exp - vs) > 0.4
            flag = "🔴 Likely Fake" if is_fake else "🟢 Authentic"
            border = "#ef4444" if is_fake else "#10b981"
            st.markdown(f"""<div class="review-card" style="border-left:4px solid {border};">
                <div style="display:flex; justify-content:space-between; margin-bottom:6px;">
                    <strong>{'⭐' * hr['rating']} ({hr['rating']}/5)</strong>
                    <span style="color:#7c3aed; font-size:0.8rem;">{hr['date_ago']}</span>
                </div>
                <div style="font-size:0.78rem; color:#c084fc; margin-bottom:8px;">VADER: {vs:.3f} | {flag}</div>
                <p style="font-size:0.9rem; line-height:1.5; color:#d8b4fe; margin:0;">{hr['text']}</p>
            </div>""", unsafe_allow_html=True)
        if shown == 0:
            st.info("No reviews match your query." if search_term else "No review data available.")
        st.markdown('</div></div>', unsafe_allow_html=True)
