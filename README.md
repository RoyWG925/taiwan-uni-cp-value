# 大學科系「CP 值」大檢驗

> 錄取分數越高，畢業薪資真的越高嗎？— 資料科學在教育上的應用 期末專題
> 作者：41111017E 王語揚 ・ 指導：張維元 教授

互動式網站結合 **大考分發 114 學年錄取資料**（全國 1,787 校系）與 **勞動部 114 年 7 月畢業生薪資**（25 學門），
用 OLS 殘差 + P25/P50/P75 薪資分布量化「哪些學門薪資高於或低於模型預期」與「薪資的上緣與下緣」。

## 線上 Demo

🔗 部署於 Streamlit Community Cloud：（連結填這裡）

## 五個頁面

| 頁面 | 功能 |
| :--- | :--- |
| 🏠 主頁 | hero stats + 主互動散佈圖 + Top/Bottom 5 排行 |
| 🔍 查我的科系 | 輸入學校 + 系名 → 找到對應學門 → 顯示位置、薪資 P25/P50/P75、殘差解讀 |
| 📊 學門詳情 | 單一學門 drill-down：薪資分布 bar chart、校系錄取分數列表、跟其他學門比較 |
| ⚖️ 薪資分化 | 四象限視圖（高薪・高分化 vs 低薪・集中）+ 薪資分化指標排名 |
| 📖 方法論 | 資料來源、處理流程、限制與誠實聲明 |

## 在地端執行

```bash
pip install -r requirements.txt
streamlit run app.py
```

預設 http://localhost:8501。

## 資料管線（不在這個 repo 內）

完整管線在 [上一層 repo `W10/`](https://github.com/...) 內，包含：

- `parse_uac_pdf.py` — pdfplumber 解析大考分發 PDF
- `scrape_salary.py` — Playwright 抓 yoursalary Cognos
- `map_to_xuemen.py` — 校系 → 學門 對照
- `extract_quantiles.py` — 從薪資 bucket 內插 P25/P50/P75
- `analysis_v2.py` — 整合 + 出圖

本 repo 只保留**運行 Streamlit 需要的**最終資料 (`data/*.csv`)。

## 技術棧

Python 3.13 · Streamlit · Plotly · pandas · scipy · scikit-learn
