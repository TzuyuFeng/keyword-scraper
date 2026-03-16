import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse
import requests as req
from flask import Flask, render_template, request, redirect, url_for, session, flash, Response, send_file
from flask_session import Session
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_FILE_DIR"] = os.path.join(os.path.dirname(__file__), "flask_session")
Session(app)

PLATFORMS = {
    "pchome": "PChome",
    "momo":   "Momo",
    "ikea":   "IKEA",
    "bq":     "特力+",
}

MAX_LIMIT = 50

def run_scraper(platform_key, keyword, limit):
    if platform_key == "pchome":
        from scrapers.pchome import search
    elif platform_key == "momo":
        from scrapers.momo import search
    elif platform_key == "ikea":
        from scrapers.ikea import search
    elif platform_key == "bq":
        from scrapers.bq import search
    else:
        return platform_key, []
    return platform_key, search(keyword, limit)

ALLOWED_IMAGE_HOSTS = {
    "img.pchome.com.tw",                # PChome（新網域）
    "momoshop.com.tw",                  # Momo
    "www.ikea.com.tw",                   # IKEA
    "trplus.com.tw",                     # 特力+
}

@app.route("/img")
def proxy_image():
    url = request.args.get("url", "")
    if not url:
        return "", 400
    host = urlparse(url).hostname or ""
    if not any(host.endswith(h) for h in ALLOWED_IMAGE_HOSTS):
        return "", 403
    referer_map = {"a.ecimg.tw": "https://24h.pchome.com.tw/"}
    referer = next((v for k, v in referer_map.items() if host.endswith(k)), "https://www.momoshop.com.tw/")
    try:
        r = req.get(url, headers={"Referer": referer, "User-Agent": "Mozilla/5.0"}, timeout=8)
        return Response(r.content, content_type=r.headers.get("Content-Type", "image/jpeg"))
    except Exception:
        return "", 502

@app.route("/")
def index():
    return render_template("index.html", platforms=PLATFORMS, max_limit=MAX_LIMIT)

@app.route("/search", methods=["POST"])
def search():
    keyword = request.form.get("keyword", "").strip()
    selected = request.form.getlist("platforms")
    try:
        limit = int(request.form.get("limit", 10))
        limit = max(1, min(limit, MAX_LIMIT))
    except ValueError:
        limit = 10

    if not keyword:
        flash("請輸入搜尋關鍵字", "warning")
        return redirect(url_for("index"))
    if not selected:
        flash("請至少選擇一個電商平台", "warning")
        return redirect(url_for("index"))

    results = {}
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {executor.submit(run_scraper, p, keyword, limit): p for p in selected}
        for future in as_completed(futures):
            platform_key, data = future.result()
            platform_name = PLATFORMS.get(platform_key, platform_key)
            results[platform_name] = data

    session["results"] = results
    session["keyword"] = keyword
    session["limit"] = limit
    return redirect(url_for("results"))

@app.route("/results")
def results():
    results = session.get("results", {})
    keyword = session.get("keyword", "")
    limit = session.get("limit", 10)
    if not results:
        flash("請先執行搜尋", "info")
        return redirect(url_for("index"))
    return render_template("results.html", results=results, keyword=keyword, limit=limit)

@app.route("/export", methods=["POST"])
def export():
    results = session.get("results", {})
    keyword = session.get("keyword", "搜尋結果")
    if not results:
        flash("沒有可匯出的資料", "warning")
        return redirect(url_for("index"))

    try:
        from services.excel import export as excel_export
        output = excel_export(keyword, results)
        filename = f"熱賣商品_{keyword}.xlsx"
        return send_file(
            output,
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            as_attachment=True,
            download_name=filename,
        )
    except Exception as e:
        flash(f"匯出失敗：{str(e)}", "danger")
        return redirect(url_for("results"))

if __name__ == "__main__":
    app.run(debug=True, port=5001)
