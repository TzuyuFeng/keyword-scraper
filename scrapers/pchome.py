import requests
import time

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def search(keyword, limit=10):
    url = "https://ecshweb.pchome.com.tw/search/v3.3/all/results"
    params = {"q": keyword, "sort": "sale/dc", "page": 1}

    try:
        resp = requests.get(url, params=params, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        return [{"error": str(e)}]

    products = []
    for i, item in enumerate(data.get("prods", [])[:limit], start=1):
        pic = item.get("picS", "")
        image_url = f"https://a.ecimg.tw{pic}" if pic else ""
        prod_id = item.get("Id", "")
        products.append({
            "platform": "PChome",
            "rank": i,
            "name": item.get("name", ""),
            "price": item.get("price", 0),
            "sales": "N/A",
            "image_url": image_url,
            "product_url": f"https://24h.pchome.com.tw/prod/{prod_id}" if prod_id else ""
        })

    time.sleep(0.5)
    return products
