import requests
import time

def search(keyword, limit=10):
    url = "https://shopee.tw/api/v4/search/search_items"
    params = {
        "keyword": keyword,
        "by": "sales",
        "limit": limit,
        "order": "desc",
        "page_type": "search",
        "newest": 0,
        "version": 2
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": f"https://shopee.tw/search?keyword={keyword}",
        "X-API-SOURCE": "pc",
        "X-Requested-With": "XMLHttpRequest"
    }

    try:
        resp = requests.get(url, params=params, headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        return [{"error": str(e)}]

    items = []
    sections = data.get("data", {}).get("sections", [])
    for section in sections:
        items.extend(section.get("data", {}).get("item", []))
    items = items[:limit]

    products = []
    for i, item in enumerate(items, start=1):
        image = item.get("image", "")
        image_url = f"https://cf.shopee.tw/file/{image}" if image else ""
        shopid = item.get("shopid", "")
        itemid = item.get("itemid", "")
        price_raw = item.get("price", 0)
        price = price_raw // 100000 if price_raw else 0
        sales = item.get("historical_sold", item.get("sold", "N/A"))
        products.append({
            "platform": "蝦皮",
            "rank": i,
            "name": item.get("name", ""),
            "price": price,
            "sales": sales if sales else "N/A",
            "image_url": image_url,
            "product_url": f"https://shopee.tw/product/{shopid}/{itemid}" if shopid else ""
        })

    time.sleep(0.5)
    return products
