"""共用 CSS + helper — 讓 5 個頁面 look consistent。"""
import streamlit as st


def inject_global_css():
    """全頁面共用：載入字型、隱藏雜訊元件、調整 spacing。"""
    st.markdown('''
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@300;400;500;600;700&family=Outfit:wght@400;500;600;700&display=swap" rel="stylesheet">

<style>
/* ── 字型：中文 Noto Sans TC + 英文 Outfit ── */
html, body, [class*="css"], .stApp {
    font-family: 'Outfit', 'Noto Sans TC', -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}

/* ── 隱藏 Streamlit Cloud 的浮動元件 ── */
.stDeployButton { display: none !important; }
[data-testid="stStatusWidget"] { display: none !important; }
footer { visibility: hidden; }
.viewerBadge_container__1QSob { display: none !important; }
[data-testid="stToolbar"] { display: none !important; }

/* ── 標題：更厚實的字重 ── */
h1 {
    font-weight: 700 !important;
    letter-spacing: -0.01em;
}
h2 {
    font-weight: 600 !important;
    border-bottom: 2px solid #0E4D92;
    padding-bottom: 0.3em;
    margin-top: 1.8em !important;
}
h3 {
    font-weight: 600 !important;
    color: #0E4D92;
    margin-top: 1.5em !important;
}

/* ── Metric 卡片 ── */
[data-testid="stMetric"] {
    background: white;
    border: 1px solid #E0DCC8;
    border-radius: 6px;
    padding: 14px 18px;
    box-shadow: 0 1px 2px rgba(0,0,0,0.03);
}
[data-testid="stMetricLabel"] {
    font-weight: 500;
    color: #555;
}
[data-testid="stMetricValue"] {
    font-weight: 700;
    color: #0E4D92;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #1A1A1A;
}
[data-testid="stSidebar"] *, [data-testid="stSidebar"] a {
    color: #FAFAF7 !important;
}
[data-testid="stSidebar"] [data-testid="stSidebarNav"] a {
    border-radius: 4px;
    transition: background 0.2s;
}
[data-testid="stSidebar"] [data-testid="stSidebarNav"] a:hover {
    background: rgba(255,255,255,0.08) !important;
}


/* ── DataFrame 卡片化 ── */
[data-testid="stDataFrame"] {
    border-radius: 6px;
    border: 1px solid #E0DCC8;
    overflow: hidden;
}

/* ── 主內容區更舒服的邊距 ── */
.block-container {
    padding-top: 2.5rem !important;
    padding-bottom: 4rem !important;
    max-width: 1280px !important;
}

/* ── selectbox / button 統一邊框 ── */
[data-testid="stSelectbox"] > div > div,
[data-testid="stMultiSelect"] > div > div {
    border: 1px solid #C8C2B0 !important;
    background: white !important;
}

/* ── info/success/warning callout ── */
[data-testid="stAlert"] {
    border-radius: 6px;
    border-left-width: 4px;
}

/* ── divider 細一點 ── */
hr {
    border-color: #D8D3C0 !important;
    margin: 1.5em 0 !important;
}

/* ── plotly chart 邊框 ── */
.js-plotly-plot {
    border-radius: 6px;
    background: white;
    padding: 8px;
    border: 1px solid #E0DCC8;
}
</style>
''', unsafe_allow_html=True)


def hero(title: str, subtitle: str = '', icon: str = ''):
    """畫一個自訂 hero 區塊（比 st.title 漂亮）。"""
    st.markdown(f'''
<div style="
    background: linear-gradient(135deg, #0E4D92 0%, #1A6BB8 100%);
    color: white;
    padding: 2.2rem 2.4rem;
    border-radius: 8px;
    margin-bottom: 1.6rem;
    box-shadow: 0 4px 12px rgba(14,77,146,0.18);
">
    <div style="font-size: 0.9rem; opacity: 0.85; letter-spacing: 0.05em; text-transform: uppercase;">
        {icon} 資料科學在教育上的應用 · 期末專題
    </div>
    <h1 style="
        color: white;
        margin: 0.5rem 0 0.3rem 0;
        font-weight: 700;
        font-size: 2.4rem;
        letter-spacing: -0.02em;
    ">{title}</h1>
    {f'<div style="font-size: 1.15rem; opacity: 0.92; font-weight: 400;">{subtitle}</div>' if subtitle else ''}
</div>
''', unsafe_allow_html=True)
