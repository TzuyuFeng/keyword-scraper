import os
import gspread
from google.oauth2.service_account import Credentials

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

SHEET_TITLE = "電商熱賣搜尋結果"

def get_client():
    cred_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "credentials.json")
    if not os.path.exists(cred_path):
        raise FileNotFoundError("找不到 credentials.json，請先設定 Google API 憑證")
    creds = Credentials.from_service_account_file(cred_path, scopes=SCOPES)
    return gspread.authorize(creds)

def export(keyword, results_by_platform):
    client = get_client()

    # 取得或建立固定試算表（Drive 只保留一份）
    try:
        spreadsheet = client.open(SHEET_TITLE)
        # 刪除所有多餘工作表，只保留第一個
        worksheets = spreadsheet.worksheets()
        for ws in worksheets[1:]:
            spreadsheet.del_worksheet(ws)
        spreadsheet.sheet1.clear()
        spreadsheet.sheet1.update_title("工作表1")  # 重設名稱以備後續重命名
    except gspread.exceptions.SpreadsheetNotFound:
        spreadsheet = client.create(SHEET_TITLE)
        # 新建後設為任何人可讀
        spreadsheet.share(None, perm_type="anyone", role="reader")

    first = True
    for platform, products in results_by_platform.items():
        if first:
            ws = spreadsheet.sheet1
            ws.update_title(platform)
            first = False
        else:
            ws = spreadsheet.add_worksheet(title=platform, rows=100, cols=10)

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

        # 標題列加粗、凍結
        ws.format("A1:F1", {"textFormat": {"bold": True}})
        ws.freeze(rows=1)

    return spreadsheet.url
