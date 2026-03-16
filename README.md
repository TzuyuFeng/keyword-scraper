# 電商熱賣商品搜尋器

輸入關鍵字，同時搜尋多個電商平台的熱賣商品，依銷量排序，一鍵下載含圖片的 Excel 報表。

## 支援平台

| 平台 | 方法 | 排序 | 速度 |
|------|------|------|------|
| PChome | 官方 JSON API | 銷量降冪 | ⚡ 快（1–2 秒） |
| Momo | Playwright 瀏覽器自動化 | 預設熱門 | 🐌 約 15 秒 |
| IKEA | Playwright 瀏覽器自動化 | 銷量（`sort=SALES`） | 🐌 約 15 秒 |
| 特力+ | Playwright 瀏覽器自動化 | 預設排序 | 🐌 約 15 秒 |

## 功能

- 複選電商平台（可同時選多個）
- 自訂搜尋筆數（1–50 筆，依銷量排序）
- 商品卡片顯示（圖片、名稱、價格）
- 一鍵下載 Excel（`.xlsx`），含嵌入式商品圖片、可點擊商品連結

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

### 3. 搜尋並匯出

1. 勾選平台、輸入關鍵字、設定筆數，按「搜尋」
2. 搜尋完成後點「**下載 Excel**」
3. 瀏覽器自動下載 `熱賣商品_{關鍵字}.xlsx`

> 不需要任何 Google 帳號或 API 設定。

## Excel 報表格式

| 欄位 | 說明 |
|------|------|
| 排名 | 搜尋結果名次 |
| 圖片 | 嵌入商品縮圖（100×100 px） |
| 商品名稱 | 完整商品標題 |
| 價格(NT$) | 售價 |
| 銷量 | 銷售數量（Momo / IKEA / 特力+ 為 N/A） |
| 商品連結 | 可點擊超連結，直接開啟商品頁面 |

- 每個平台各一個工作表
- 標題列深藍底白字、凍結首列

## 檔案結構

```
keyword-scraper/
├── app.py                  # Flask 主程式（路由、圖片代理、Excel 匯出）
├── scrapers/
│   ├── pchome.py           # PChome 官方 API（requests）
│   ├── momo.py             # Momo 爬蟲（Playwright，goodsimg 圖片過濾）
│   ├── ikea.py             # IKEA 爬蟲（Playwright，.itemBlock，sort=SALES）
│   └── bq.py               # 特力+ 爬蟲（Playwright，<a> 商品卡）
├── services/
│   └── excel.py            # Excel 匯出（openpyxl + Pillow 嵌入圖片）
├── templates/
│   ├── base.html           # 共用版型（Navbar、Bootstrap 5）
│   ├── index.html          # 搜尋表單
│   └── results.html        # 結果卡片 + 下載按鈕
├── static/
│   ├── css/custom.css
│   └── js/main.js
├── requirements.txt
└── .gitignore
```

## 注意事項

- 各平台為非官方爬蟲，若平台更新 HTML 結構可能需要調整選擇器
- Momo / IKEA / 特力+ 使用 Playwright 模擬真實瀏覽器，速度較慢
- Excel 匯出時需下載所有商品圖片，筆數越多耗時越長
- PChome 圖片網域：`img.pchome.com.tw/cs`（2025 年後更新）
- 蝦皮已移除（反爬蟲機制封鎖）

## GitHub

專案連結：[https://github.com/TzuyuFeng/keyword-scraper](https://github.com/TzuyuFeng/keyword-scraper)

```bash
cd D:\Claude\keyword-scraper
git add .
git commit -m "說明"
git push origin main
```
