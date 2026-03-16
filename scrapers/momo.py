from urllib.parse import quote
from playwright.sync_api import sync_playwright

def search(keyword, limit=10):
    products = []
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=["--disable-blink-features=AutomationControlled", "--no-sandbox"]
            )
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                locale="zh-TW",
                viewport={"width": 1280, "height": 800}
            )
            context.add_init_script(
                "Object.defineProperty(navigator, 'webdriver', { get: () => undefined });"
            )
            page = context.new_page()
            url = f"https://www.momoshop.com.tw/search/searchShop.jsp?keyword={quote(keyword)}&searchType=1&curPage=1&_isFuzzy=0&showType=chessBoard"
            page.goto(url, timeout=30000)
            page.wait_for_timeout(5000)

            data = page.evaluate(f"""() => {{
                const items = document.querySelectorAll("li.listAreaLi");
                const out = [];
                for (let i = 0; i < Math.min({limit}, items.length); i++) {{
                    const el = items[i];
                    const name = el.querySelector(".prdName")?.innerText?.trim() || "";
                    if (!name) continue;
                    const priceEl = el.querySelector(".price b") || el.querySelector("b.price") || el.querySelector("[class*='price'] b");
                    const price = priceEl?.innerText?.trim().replace(/,/g, "") || "0";
                    // Momo 商品主圖 URL 路徑含 /goods/，促銷 badge 不含
                    let img = "";
                    const imgCandidates = el.querySelectorAll("img");
                    for (const imgEl of imgCandidates) {{
                        const src = imgEl?.src || imgEl?.dataset?.src || imgEl?.dataset?.lazySrc || "";
                        if (!src) continue;
                        if (/goodsimg/i.test(src)) {{ img = src; break; }}
                        if (!img && /momoshop\.com\.tw/i.test(src)) img = src;
                    }}
                    const linkEl = el.querySelector("a[href*='goods'], a[href*='product'], a[href*='GoodsDetail']");
                    const href = linkEl?.href || "";
                    out.push({{ name, price, img, href }});
                }}
                return out;
            }}""")

            browser.close()

        for i, item in enumerate(data, start=1):
            try:
                price = int(item.get("price", "0").replace(",", ""))
            except ValueError:
                price = 0

            image_url = item.get("img", "")
            # 確保圖片 URL 完整
            if image_url and not image_url.startswith("http"):
                image_url = "https:" + image_url

            products.append({
                "platform": "Momo",
                "rank": i,
                "name": item.get("name", ""),
                "price": price,
                "sales": "N/A",
                "image_url": image_url,
                "product_url": item.get("href", "")
            })

    except Exception as e:
        return [{"error": str(e)}]

    if not products:
        return [{"error": "Momo 搜尋結果為空"}]
    return products
