# 股票分析報告

此資料夾包含自動生成的股票分析報告。

## 📊 報告類型

### 匯總報告
- `summary.html` - 多股票比較匯總報告（如果分析多個股票）

### 個股報告
每個股票會生成以下文件：
- `report_XXXX.html` - 詳細分析報告（**點擊此文件查看**）
- `chart_price_XXXX.png` - 價格走勢圖
- `chart_institutional_XXXX.png` - 三大法人買賣超圖
- `report_XXXX.md` - Markdown 格式報告
- `result_XXXX.json` - 原始數據

## 🔍 如何查看報告

### 方法 1: 直接在 GitHub 查看
1. 點擊 `report_XXXX.html` 文件
2. 點擊右上角的 "Raw" 按鈕
3. 複製 URL
4. 在新分頁貼上: `https://htmlpreview.github.io/?` + 你的 Raw URL

### 方法 2: 下載到本地
1. 點擊 `Code` → `Download ZIP`
2. 解壓縮後打開 `reports` 資料夾
3. 雙擊 `report_XXXX.html` 即可在瀏覽器中查看

### 方法 3: 使用 GitHub Pages（推薦）
如果啟用了 GitHub Pages，可以直接訪問：
`https://你的用戶名.github.io/stockv2/reports/report_XXXX.html`

## 📅 更新頻率

報告由 GitHub Actions 自動生成，每次手動觸發工作流程時更新。

## 🎯 最新報告

查看最新的 commit 訊息以了解報告生成時間。
