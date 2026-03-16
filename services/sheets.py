import os
import gspread
from google.oauth2.service_account import Credentials

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

def get_client():
    cred_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "credentials.json")
    if not os.path.exists(cred_path):
        raise FileNotFoundError("找不到 credentials.json，請先設定 Google API 憑證")
    creds = Credentials.from_service_account_file(cred_path, scopes=SCOPES)
    return gspread.authorize(creds)

def cleanup_old_sheets(client):
    """刪除服務帳戶 Drive 中所有舊的搜尋試算表，避免超出配額"""
    try:
        files = client.list_spreadsheet_files()
        for f in files:
            if "熱賣商品搜尋" in f.get("name", ""):
                client.del_spreadsheet(f["id"])
    except Exception:
        pass  # 清理失敗不影響主流程

def export(keyword, results_by_platform):
    client = get_client()
    title = f"熱賣商品搜尋 - {keyword}"

    # 建立前先清理舊試算表，釋放 Drive 空間
    cleanup_old_sheets(client)

    spreadsheet = client.create(title)

    first = True
    for platform, products in results_by_platform.items():
        if first:
            ws = spreadsheet.sheet1
            ws.update_title(platform)
            first = False
        else:
            ws = spreadsheet.add_worksheet(title=platform, rows=50, cols=10)

        headers = ["排名", "圖片", "商品名稱", "價格(NT$)", "銷量", "商品連結"]
        ws.append_row(headers)

        for p in products:
            image_formula = f'=IMAGE("{p["image_url"]}")' if p.get("image_url") else ""
            ws.append_row([
                p.get("rank", ""),
                image_formula,
                p.get("name", ""),
                p.get("price", ""),
                p.get("sales", "N/A"),
                p.get("product_url", "")
            ])

        # 調整列高讓圖片可見
        ws.format("A1:F1", {"textFormat": {"bold": True}})
        ws.freeze(rows=1)

    # 設定試算表為任何人可讀（方便分享）
    spreadsheet.share(None, perm_type="anyone", role="reader")

    return spreadsheet.url
