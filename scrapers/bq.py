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
                viewport={"width": 1280, "height": 900}
            )
            context.add_init_script(
                "Object.defineProperty(navigator, 'webdriver', { get: () => undefined });"
            )
            page = context.new_page()
            q = quote(keyword)
            url = f"https://www.trplus.com.tw/search?sort=sale_qty-desc&q={q}&text={q}"
            page.goto(url, timeout=30000)
            try:
                page.wait_for_load_state("networkidle", timeout=12000)
            except Exception:
                pass
            page.wait_for_timeout(3000)
            page.evaluate("window.scrollTo(0, 600)")
            page.wait_for_timeout(1000)

            data = page.evaluate(f"""() => {{
                // 特力+ 的 <A> 本身就是商品卡（class 含 product-card）
                // 直接找有圖片且連結到 /p/ 的 <a> 元素
                const allLinks = Array.from(document.querySelectorAll('a[href*="/p/"]'));
                // 只保留本身含有圖片的 <a>（商品卡），排除純文字連結
                const productCards = allLinks.filter(a => a.querySelector('img') && a.innerText.length > 5);

                const seen = new Set();
                const out = [];

                for (const link of productCards) {{
                    const href = link.href;
                    if (seen.has(href)) continue;
                    seen.add(href);

                    // 名稱：<a> 內第一行非空文字
                    const lines = (link.innerText || '').split('\\n')
                                    .map(l => l.trim()).filter(l => l.length > 0);
                    const name = lines[0] || '';
                    if (!name || name.length < 2) continue;

                    // 價格：第一個 $數字（現售價）
                    const priceMatch = (link.innerText || '').match(/\$([0-9,]+)/);
                    const price = priceMatch ? priceMatch[1].replace(/,/g, '') : '0';

                    // 圖片：<a> 內第一張 img（650x650 高解析度版）
                    const imgEl = link.querySelector('img');
                    const img = imgEl?.src || imgEl?.dataset?.src || '';

                    out.push({{ name, price, img, href }});
                    if (out.length >= {limit}) break;
                }}
                return out;
            }}""")

            browser.close()

        for i, item in enumerate(data, 1):
            image_url = item.get("img", "")
            if image_url and not image_url.startswith("http"):
                image_url = "https:" + image_url
            products.append({
                "platform": "特力+",
                "rank": i,
                "name": item.get("name", ""),
                "price": int(item.get("price", "0") or 0),
                "sales": "N/A",
                "image_url": image_url,
                "product_url": item.get("href", ""),
            })

    except Exception as e:
        return [{"error": str(e)}]

    if not products:
        return [{"error": "特力+ 搜尋結果為空"}]
    return products
