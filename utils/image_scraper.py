"""Image scraper — fetches real product/hotel images via DuckDuckGo with caching."""
import json, hashlib, time
from pathlib import Path

CACHE_DIR = Path(__file__).resolve().parent.parent / "outputs" / "image_cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

def _cache_path(query: str) -> Path:
    return CACHE_DIR / f"{hashlib.md5(query.lower().strip().encode()).hexdigest()}.json"

def fetch_image_url(query: str, suffix: str = "") -> str:
    full = f"{query} {suffix}".strip()
    cache = _cache_path(full)
    if cache.exists():
        try:
            d = json.loads(cache.read_text(encoding="utf-8"))
            if d.get("url"): return d["url"]
        except: pass
    try:
        from duckduckgo_search import DDGS
        with DDGS() as ddgs:
            results = list(ddgs.images(full, max_results=3))
            if results:
                url = results[0].get("image", "") or results[0].get("thumbnail", "")
                if url:
                    cache.write_text(json.dumps({"url": url, "query": full}), encoding="utf-8")
                    return url
    except Exception as e:
        print(f"⚠️ Image search failed for '{full}': {e}")
    return ""

def get_entity_image(name: str, entity_type: str = "product") -> str:
    suffix = "restaurant hotel exterior photo" if entity_type in ("hotel","restaurant","yelp") else "product photo"
    return fetch_image_url(name, suffix)
