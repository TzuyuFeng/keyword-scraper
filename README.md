# 電商熱賣商品搜尋器

輸入關鍵字，同時搜尋多個電商平台的熱賣商品，依銷量排序，一鍵匯出至 Google 試算表（含圖片）。

## 支援平台

| 平台 | 方法 | 速度 |
|------|------|------|
| PChome | 官方 JSON API | ⚡ 快（1–2 秒） |
| Momo | Playwright 瀏覽器自動化 | 🐌 約 15 秒 |
| IKEA | Playwright 瀏覽器自動化 | 🐌 約 15 秒 |
| 特力+ | Playwright 瀏覽器自動化 | 🐌 約 15 秒 |

## 功能

- 複選電商平台（可同時選多個）
- 自訂搜尋筆數（1–50 筆，依銷量排序）
- 商品卡片顯示（圖片、名稱、價格）
- 一鍵匯出至 Google 試算表（含 `=IMAGE()` 圖片公式）

## 快速開始

### 1. 建立虛擬環境並安裝套件

```bash
python -m venv .venv
.venv\Scripts\activate       # Windows
pip install -r requirements.txt
playwright install chromium  # 下載瀏覽器（約 300MB）
```

### 2. 啟動伺服器

```bash
python app.py
# 瀏覽 http://127.0.0.1:5001
```

> 不需要設定 Google Sheets 也能正常搜尋，匯出功能為選用。

### 3. 設定 Google Sheets 匯出（選用）

1. 前往 [Google Cloud Console](https://console.cloud.google.com)
2. 建立新專案（任意命名）
3. 啟用 **Google Sheets API** 與 **Google Drive API**
4. 建立「服務帳戶」憑證 → 下載 JSON 金鑰
5. 將 JSON 檔案重新命名為 **`credentials.json`**，放入本專案根目錄

> ⚠️ `credentials.json` 已加入 `.gitignore`，不會上傳至 GitHub

## 檔案結構

```
keyword-scraper/
├── app.py                  # Flask 主程式（路由、圖片代理、匯出）
├── scrapers/
│   ├── pchome.py           # PChome 官方 API（requests）
│   ├── momo.py             # Momo 爬蟲（Playwright）
│   ├── ikea.py             # IKEA 爬蟲（Playwright，.itemBlock）
│   └── bq.py               # 特力+ 爬蟲（Playwright，<a> 商品卡）
├── services/
│   └── sheets.py           # Google Sheets 匯出
├── templates/
│   ├── base.html           # 共用版型（Navbar、Bootstrap）
│   ├── index.html          # 搜尋表單
│   └── results.html        # 結果卡片
├── static/
│   ├── css/custom.css
│   └── js/main.js
├── requirements.txt
└── .gitignore
```

## 注意事項

- 各平台為非官方爬蟲，若平台更新 HTML 結構可能需要調整選擇器
- Momo / IKEA / 特力+ 使用 Playwright 模擬真實瀏覽器，速度較慢
- PChome 圖片網域：`img.pchome.com.tw/cs`（2025 年後更新）
- 蝦皮已移除（反爬蟲機制封鎖）

## GitHub

專案連結：[https://github.com/TzuyuFeng/keyword-scraper](https://github.com/TzuyuFeng/keyword-scraper)

```bash
# 推送至 GitHub
git add .
git commit -m "說明"
git push origin main
```
