import requests
import time
import math

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}
PER_PAGE = 20

def search(keyword, limit=10):
    products = []
    pages_needed = math.ceil(limit / PER_PAGE)

    for page in range(1, pages_needed + 1):
        url = "https://ecshweb.pchome.com.tw/search/v3.3/all/results"
        params = {"q": keyword, "sort": "sale/dc", "page": page}
        try:
            resp = requests.get(url, params=params, headers=HEADERS, timeout=10)
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            if not products:
                return [{"error": str(e)}]
            break

        prods = data.get("prods", [])
        if not prods:
            break

        for item in prods:
            if len(products) >= limit:
                break
            pic = item.get("picS", "")
            image_url = f"https://img.pchome.com.tw/cs{pic}" if pic else ""
            prod_id = item.get("Id", "")
            products.append({
                "platform": "PChome",
                "rank": len(products) + 1,
                "name": item.get("name", ""),
                "price": item.get("price", 0),
                "sales": "N/A",
                "image_url": image_url,
                "product_url": f"https://24h.pchome.com.tw/prod/{prod_id}" if prod_id else ""
            })

        if page < pages_needed:
            time.sleep(0.3)

    return products
