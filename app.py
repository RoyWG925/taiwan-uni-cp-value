"""
大學科系 CP 值大檢驗 — 互動式探索網站
作者：41111017E 王語揚
課程：資料科學在教育上的應用（114 學年下學期）

主頁 (Overview)：說明 + hero 散佈圖 + top/bottom 學門。
"""
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

DATA = Path(__file__).parent / 'data'

# ─────────────────────────────────────────────────────────
# Page config
# ─────────────────────────────────────────────────────────
st.set_page_config(
    page_title='大學科系 CP 值大檢驗',
    page_icon='🎓',
    layout='wide',
    initial_sidebar_state='expanded',
)


# ─────────────────────────────────────────────────────────
# Data loaders (cached)
# ─────────────────────────────────────────────────────────
@st.cache_data
def load_final_v2():
    return pd.read_csv(DATA / 'final_dataset_v2.csv')


@st.cache_data
def load_uac():
    return pd.read_csv(DATA / 'uac_with_xuemen.csv',
                       dtype={'系組代碼': str})


@st.cache_data
def load_salary():
    return pd.read_csv(DATA / 'salary_with_quantiles.csv')


df = load_final_v2()

# ─────────────────────────────────────────────────────────
# Sidebar (shared across pages)
# ─────────────────────────────────────────────────────────
with st.sidebar:
    st.title('🎓 CP 值大檢驗')
    st.caption('資料來源：UAC 114 學年 + 勞動部 114/07 + 教育部')
    st.divider()
    st.markdown('''
**頁面導覽**
- 🏠 **主頁**：整體故事 + 互動散佈圖
- 🔍 **查我的科系**：輸入學校系名找位置
- 📊 **學門詳情**：單一學門深入
- ⚖️ **風險探索**：薪資離散度比較
- 📖 **方法論**：資料來源與限制
''')
    st.divider()
    st.caption('41111017E 王語揚')


# ─────────────────────────────────────────────────────────
# Header
# ─────────────────────────────────────────────────────────
st.title('🎓 大學科系「CP 值」大檢驗')
st.subheader('錄取分數越高，畢業薪資真的越高嗎？')

st.markdown('''
本研究結合 **大學分發委員會 114 學年錄取分數** 與 **勞動部 114 年 7 月畢業生薪資**，
用真實資料檢驗一個所有高中生都想問的問題：
> 分數越高的科系，畢業後薪水真的越高嗎？
''')

# Hero stats
c1, c2, c3, c4 = st.columns(4)
c1.metric('分析學門數', f"{len(df)} 類", help='25 個教育部標準學門大類')
c2.metric('涵蓋校系', '1,772 個', help='114 學年大考分發所有有效校系')
c3.metric('涵蓋勞工', f"{df['employed_n'].sum():,} 人",
          help='勞動部勞退提繳系統內所有 114/07 在職畢業生')
r2_val = 0.219
c4.metric('PR 解釋力 (R²)', f'{r2_val:.3f}',
          help='中位錄取分數百分位對 P50 薪資的解釋變異')

st.divider()


# ─────────────────────────────────────────────────────────
# Main interactive scatter
# ─────────────────────────────────────────────────────────
st.markdown('## 📍 主互動散佈圖')
st.markdown(
    '每個點代表一個 **學門大類**，X 軸是中位錄取分數百分位（越右越難進）'
    '、Y 軸是 P50 薪資中位數，誤差棒是 P25–P75 區間。'
)

# Filters
with st.expander('🔧 篩選 / 顯示選項', expanded=False):
    fc1, fc2, fc3 = st.columns(3)
    groups_filter = fc1.multiselect(
        '三分群（過濾）',
        options=['應用 STEM', '基礎 STEM', '人文社科'],
        default=['應用 STEM', '基礎 STEM', '人文社科'],
    )
    show_err = fc2.checkbox('顯示 P25–P75 誤差棒', value=True)
    show_ols = fc3.checkbox('顯示 OLS 回歸線', value=True)

shown = df[df['三分群'].isin(groups_filter)].copy()
shown['hover_text'] = shown.apply(lambda r: (
    f"<b>{r['學門']}</b><br>"
    f"中位 PR 百分位：{r['median_pr_pct']:.1f}<br>"
    f"P25 / P50 / P75：{r['P25']:,} / {r['P50']:,} / {r['P75']:,} 元<br>"
    f"風險指標：{r['風險指標']:.3f}<br>"
    f"OLS 殘差：{r['residual_P50']:+,} 元<br>"
    f"勞工人數：{r['employed_n']:,}"
), axis=1)

palette = {'應用 STEM': '#1f77b4', '基礎 STEM': '#2ca02c', '人文社科': '#d62728'}

fig = go.Figure()
for g, sub in shown.groupby('三分群'):
    err_y = dict(
        type='data', symmetric=False,
        array=(sub['P75'] - sub['P50']),
        arrayminus=(sub['P50'] - sub['P25']),
        thickness=1.5, width=4,
    ) if show_err else None

    fig.add_trace(go.Scatter(
        x=sub['median_pr_pct'], y=sub['P50'],
        mode='markers+text',
        text=sub['short_name'],
        textposition='top center',
        textfont=dict(size=10),
        marker=dict(
            size=14, color=palette[g],
            line=dict(width=1, color='white'),
        ),
        error_y=err_y,
        name=g,
        hovertext=sub['hover_text'],
        hoverinfo='text',
    ))

if show_ols and len(shown) >= 2:
    from scipy import stats
    slope, intercept, *_ = stats.linregress(
        shown['median_pr_pct'], shown['P50'].astype(float))
    xs = [shown['median_pr_pct'].min() - 3, shown['median_pr_pct'].max() + 3]
    fig.add_trace(go.Scatter(
        x=xs, y=[slope * x + intercept for x in xs],
        mode='lines', line=dict(dash='dash', color='black', width=1.5),
        name=f'OLS: y = {slope:.0f}·PR + {intercept:,.0f}',
        hoverinfo='skip',
    ))

fig.update_layout(
    xaxis_title='中位錄取分數百分位（UAC 114 學年）',
    yaxis_title='P50 中位薪資 (元/月)',
    yaxis=dict(tickformat=',', range=[28_000, 90_000]),
    height=620,
    legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='left', x=0),
    margin=dict(l=60, r=40, t=30, b=60),
)
st.plotly_chart(fig, use_container_width=True)


# ─────────────────────────────────────────────────────────
# Top/Bottom 5 highlight
# ─────────────────────────────────────────────────────────
st.divider()
st.markdown('## 📈 被低估 / 被高估 排行 (Top 5 each)')

top5 = df.nlargest(5, 'residual_P50')[
    ['short_name', '三分群', 'median_pr_pct', 'P50', 'residual_P50']].copy()
bot5 = df.nsmallest(5, 'residual_P50')[
    ['short_name', '三分群', 'median_pr_pct', 'P50', 'residual_P50']].copy()


def fmt(d):
    d = d.copy()
    d.columns = ['學門', '三分群', '中位 PR', 'P50 薪資', '殘差']
    d['P50 薪資'] = d['P50 薪資'].apply(lambda v: f'{v:,}')
    d['殘差'] = d['殘差'].apply(lambda v: f'{v:+,}')
    return d


col_a, col_b = st.columns(2)
with col_a:
    st.markdown('### 🔵 被低估 — 同 PR 應得卻拿更多')
    st.dataframe(fmt(top5), hide_index=True, use_container_width=True)
with col_b:
    st.markdown('### 🔴 被高估 — 同 PR 應得卻拿更少')
    st.dataframe(fmt(bot5), hide_index=True, use_container_width=True)

st.info('''
**幾個直覺反差**：
- **物理、化學及地球科學**: PR 中位才 57，但 P50 達 60,696 元 — 半導體 / 材料產業帶動的薪資溢酬。
- **獸醫**: PR 高達 92（25 學門最高），但 P50 只有 42,377 元 — 可能跟「自雇獸醫不在勞退統計內」的選擇偏誤有關。
- **藝術**: PR 46，P50 只有 34,298 元，是 25 學門最低 — 「分數中段、薪資底層」的代表。
''')


# ─────────────────────────────────────────────────────────
# Footer
# ─────────────────────────────────────────────────────────
st.divider()
st.markdown('''
###### 🔗 延伸閱讀
- 左側「**查我的科系**」可輸入自己的學校與系名，自動定位
- 左側「**風險探索**」用薪資離散度看「贏家通吃」vs「保守型」學門
- 左側「**方法論**」說明資料來源、限制與誠實聲明
''')
