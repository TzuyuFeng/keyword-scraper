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
            url = f"https://www.ikea.com.tw/zh/search?q={quote(keyword)}&sort=SALES"
            page.goto(url, timeout=40000)
            try:
                page.wait_for_load_state("networkidle", timeout=12000)
            except Exception:
                pass
            page.wait_for_timeout(3000)

            # 捲動觸發 lazy loading
            page.evaluate("window.scrollTo(0, 800)")
            page.wait_for_timeout(2000)

            data = page.evaluate(f"""() => {{
                // 每個商品卡是 div.itemBlock
                const cards = Array.from(document.querySelectorAll('.itemBlock'));
                if (cards.length === 0) return [];

                const out = [];
                for (let i = 0; i < Math.min({limit}, cards.length); i++) {{
                    const el = cards[i];

                    // 名稱：第一行非空文字
                    const lines = (el.innerText || '').split('\\n')
                                    .map(l => l.trim()).filter(l => l.length > 0);
                    const name = lines[0] || '';
                    if (!name || name.length < 2) continue;

                    // 價格：IKEA 把 $ 和數字拆成兩行，換行改空格（避免數字與評分0合併）
                    const flatText = (el.innerText || '').replace(/\\n/g, ' ');
                    const priceMatch = flatText.match(/\$\s*([0-9,]+)/);
                    const price = priceMatch ? priceMatch[1].replace(/,/g, '') : '0';

                    const imgEl = el.querySelector('img');
                    const img = imgEl?.src || imgEl?.dataset?.src || '';

                    const linkEl = el.querySelector('a');
                    const href = linkEl?.href || '';

                    out.push({{ name, price, img, href }});
                }}
                return out;
            }}""")

            browser.close()

        for i, item in enumerate(data, 1):
            image_url = item.get("img", "")
            if image_url and not image_url.startswith("http"):
                image_url = "https:" + image_url
            products.append({
                "platform": "IKEA",
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
        return [{"error": "IKEA 搜尋結果為空，頁面結構可能需要調整"}]
    return products
