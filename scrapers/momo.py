import requests
import time
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "zh-TW,zh;q=0.9"
}

def search(keyword, limit=10):
    url = "https://www.momoshop.com.tw/search/searchShop.jsp"
    params = {
        "keyword": keyword,
        "searchType": 1,
        "curPage": 1,
        "_isFuzzy": 0,
        "showType": "chessBoard"
    }

    try:
        resp = requests.get(url, params=params, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
    except Exception as e:
        return [{"error": str(e)}]

    products = []
    items = soup.select("li.goodsItemLi")[:limit]

    for i, item in enumerate(items, start=1):
        name_tag = item.select_one(".prdName")
        price_tag = item.select_one(".money em") or item.select_one(".price em")
        img_tag = item.select_one("img.lazy") or item.select_one("img")
        link_tag = item.select_one("a")

        name = name_tag.get_text(strip=True) if name_tag else ""
        price_text = price_tag.get_text(strip=True).replace(",", "") if price_tag else "0"
        try:
            price = int(price_text)
        except ValueError:
            price = 0

        image_url = ""
        if img_tag:
            image_url = img_tag.get("data-src") or img_tag.get("src", "")
            if image_url.startswith("//"):
                image_url = "https:" + image_url

        product_url = ""
        if link_tag:
            href = link_tag.get("href", "")
            product_url = "https://www.momoshop.com.tw" + href if href.startswith("/") else href

        products.append({
            "platform": "Momo",
            "rank": i,
            "name": name,
            "price": price,
            "sales": "N/A",
            "image_url": image_url,
            "product_url": product_url
        })

    time.sleep(0.5)
    return products
