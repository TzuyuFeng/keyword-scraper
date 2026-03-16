import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from flask import Flask, render_template, request, redirect, url_for, session, flash
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")

PLATFORMS = {
    "pchome": "PChome",
    "shopee": "蝦皮",
    "momo": "Momo"
}

def run_scraper(platform_key, keyword):
    if platform_key == "pchome":
        from scrapers.pchome import search
    elif platform_key == "shopee":
        from scrapers.shopee import search
    elif platform_key == "momo":
        from scrapers.momo import search
    else:
        return platform_key, []
    return platform_key, search(keyword)

@app.route("/")
def index():
    return render_template("index.html", platforms=PLATFORMS)

@app.route("/search", methods=["POST"])
def search():
    keyword = request.form.get("keyword", "").strip()
    selected = request.form.getlist("platforms")

    if not keyword:
        flash("請輸入搜尋關鍵字", "warning")
        return redirect(url_for("index"))
    if not selected:
        flash("請至少選擇一個電商平台", "warning")
        return redirect(url_for("index"))

    results = {}
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {executor.submit(run_scraper, p, keyword): p for p in selected}
        for future in as_completed(futures):
            platform_key, data = future.result()
            platform_name = PLATFORMS.get(platform_key, platform_key)
            results[platform_name] = data

    session["results"] = results
    session["keyword"] = keyword
    return redirect(url_for("results"))

@app.route("/results")
def results():
    results = session.get("results", {})
    keyword = session.get("keyword", "")
    if not results:
        flash("請先執行搜尋", "info")
        return redirect(url_for("index"))
    return render_template("results.html", results=results, keyword=keyword)

@app.route("/export", methods=["POST"])
def export():
    results = session.get("results", {})
    keyword = session.get("keyword", "")
    if not results:
        flash("沒有可匯出的資料", "warning")
        return redirect(url_for("index"))

    try:
        from services.sheets import export as sheets_export
        sheet_url = sheets_export(keyword, results)
        flash(f'匯出成功！<a href="{sheet_url}" target="_blank">點此開啟 Google 試算表</a>', "success")
    except FileNotFoundError as e:
        flash(str(e), "danger")
    except Exception as e:
        flash(f"匯出失敗：{str(e)}", "danger")

    return redirect(url_for("results"))

if __name__ == "__main__":
    app.run(debug=True)
