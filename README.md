# 電商熱賣商品搜尋器

輸入關鍵字，同時搜尋 PChome / 蝦皮 / Momo 前10名熱賣商品，一鍵匯出至 Google 試算表（含圖片）。

## 功能
- 複選電商平台（PChome、蝦皮、Momo）
- 依銷量排序取前10名
- 商品卡片顯示（圖片、名稱、價格、銷量）
- 匯出至 Google 試算表（含 =IMAGE() 圖片公式）

## 快速開始

### 1. 建立虛擬環境並安裝套件
```bash
python -m venv .venv
.venv\Scripts\activate       # Windows
pip install -r requirements.txt
```

### 2. 啟動（不需要 Google Sheets 也能搜尋）
```bash
python app.py
# 瀏覽 http://127.0.0.1:5000
```

### 3. 設定 Google Sheets 匯出（選用）

> 若不需要匯出功能，跳過此步驟即可正常使用搜尋功能。

**步驟：**

1. 前往 [Google Cloud Console](https://console.cloud.google.com)
2. 建立新專案（任意命名）
3. 左側選單 → **API 和服務** → **啟用 API**
   - 搜尋並啟用 **Google Sheets API**
   - 搜尋並啟用 **Google Drive API**
4. 左側選單 → **API 和服務** → **憑證**
5. 點「建立憑證」→「服務帳戶」
   - 輸入名稱（例如：keyword-scraper）
   - 角色選「編輯者」
6. 建立後點進服務帳戶 → **金鑰** → **新增金鑰** → JSON
7. 下載的 JSON 檔案重新命名為 **`credentials.json`**，放入本專案根目錄

> ⚠️ `credentials.json` 已加入 `.gitignore`，不會上傳至 GitHub

## 檔案結構
```
keyword-scraper/
├── app.py                  # Flask 主程式
├── scrapers/
│   ├── pchome.py           # PChome 搜尋 API
│   ├── shopee.py           # 蝦皮搜尋 API
│   └── momo.py             # Momo HTML 爬蟲
├── services/
│   └── sheets.py           # Google Sheets 匯出
├── templates/              # HTML 頁面
├── static/                 # CSS / JS
├── credentials.json        # Google API 憑證（不上傳）
└── requirements.txt
```

## 注意事項
- 各平台為非官方 API，若平台更新可能需要調整
- 蝦皮搜尋需要網路連線至 shopee.tw
- Momo 依賴 HTML 結構解析，較容易受版面更新影響
