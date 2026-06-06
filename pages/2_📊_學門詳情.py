"""學門詳情：選一個學門，看它的所有 校系錄取分數分布 + 薪資 P25-P75 + 跟其他比較。"""
import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

sys.path.insert(0, str(Path(__file__).parent.parent))
from styles import inject_global_css

DATA = Path(__file__).parent.parent / 'data'

st.set_page_config(page_title='學門詳情', page_icon='📊', layout='wide')
inject_global_css()


@st.cache_data
def load_all():
    agg = pd.read_csv(DATA / 'final_dataset_v2.csv')
    uac = pd.read_csv(DATA / 'uac_with_xuemen.csv',
                      dtype={'系組代碼': str})
    sal = pd.read_csv(DATA / 'salary_with_quantiles.csv')
    return agg, uac, sal


agg, uac, sal = load_all()

st.title('📊 學門深入探索')

xuemen_options = sorted(agg['學門'].tolist())
xuemen_sel = st.selectbox('選擇學門', options=xuemen_options)

xm_row = agg[agg['學門'] == xuemen_sel].iloc[0]
sal_row = sal[sal['學門'] == xuemen_sel].iloc[0]

# ── Header stats ──
c1, c2, c3, c4 = st.columns(4)
c1.metric('三分群', xm_row['三分群'])
c2.metric('校系數', f"{xm_row['dept_count']} 個")
c3.metric('勞工總數', f"{int(xm_row['employed_n']):,} 人")
c4.metric('全國學門 P50 排名',
          f"{(agg['P50'] >= xm_row['P50']).sum()} / {len(agg)}",
          help='P50 中位薪資在 25 學門中的名次')

st.divider()

# ── Salary distribution (bucket histogram) ──
st.markdown(f'### 💰 {xuemen_sel}：薪資分佈（114/07 勞動部）')

BUCKET_LABELS = [
    '<25k', '25k–30k', '30k–35k', '35k–40k', '40k–45k', '45k–50k',
    '50k–55k', '55k–60k', '60k–70k', '70k–80k', '80k–90k', '90k–100k', '100k+'
]
bucket_cols = [f'b{i:02d}' for i in range(13)]
counts = [int(sal_row[c]) for c in bucket_cols]

# 找 P50 落在哪個 bucket，把那一根標紅
bucket_ranges = [
    (0, 25_000), (25_000, 30_000), (30_000, 35_000), (35_000, 40_000),
    (40_000, 45_000), (45_000, 50_000), (50_000, 55_000), (55_000, 60_000),
    (60_000, 70_000), (70_000, 80_000), (80_000, 90_000), (90_000, 100_000),
    (100_000, float('inf')),
]
p50_val = int(xm_row['P50'])
highlight_idx = next(
    (i for i, (lo, hi) in enumerate(bucket_ranges) if lo <= p50_val < hi),
    6)
colors = ['#1f77b4'] * 13
colors[highlight_idx] = '#d62728'

bucket_df = pd.DataFrame({'薪資區間': BUCKET_LABELS, '人數': counts})
fig_bucket = px.bar(
    bucket_df, x='薪資區間', y='人數',
    title=f'{xuemen_sel} 薪資分佈 (紅色 = P50 中位 {p50_val:,} 元所在區間)',
)
fig_bucket.update_traces(marker_color=colors)
fig_bucket.update_layout(height=400, showlegend=False)
st.plotly_chart(fig_bucket, use_container_width=True)

c1, c2, c3 = st.columns(3)
c1.metric('P25 低標', f"{int(xm_row['P25']):,} 元")
c2.metric('P50 中位', f"{int(xm_row['P50']):,} 元")
c3.metric('P75 高標', f"{int(xm_row['P75']):,} 元")

st.caption(f"風險指標 (P75-P25)/P50 = **{xm_row['風險指標']:.3f}**　|　"
           f"OLS 殘差 = **{int(xm_row['residual_P50']):+,} 元**")

st.divider()

# ── 該學門的所有校系錄取分數 ──
st.markdown(f'### 🎓 {xuemen_sel} 包含的校系 (114 學年大考分發)')

deps = uac[uac['學門'] == xuemen_sel].copy()
deps = deps[deps['錄取分數百分位'].notna()].sort_values(
    '錄取分數百分位', ascending=False)
deps_show = deps[['校名', '系組名', '錄取分數', '達成率', '錄取分數百分位', '錄取人數']].copy()
deps_show.columns = ['校名', '系組名', '錄取分數', '達成率(%)', '全國 PR 百分位', '錄取人數']
deps_show = deps_show.reset_index(drop=True)
deps_show.index = deps_show.index + 1

st.dataframe(deps_show.style.format({
    '錄取分數': '{:,.2f}',
    '達成率(%)': '{:.2f}',
    '全國 PR 百分位': '{:.2f}',
}), use_container_width=True, height=420)

# ── Histogram of校系 PR within this 學門 ──
st.markdown(f'### 📊 {xuemen_sel} 內各校系的錄取分數百分位分布')
fig_hist = px.histogram(deps, x='錄取分數百分位', nbins=18,
                        color_discrete_sequence=['#1f77b4'])
fig_hist.add_vline(x=xm_row['median_pr_pct'],
                   line_dash='dash', line_color='red',
                   annotation_text=f"中位 {xm_row['median_pr_pct']:.1f}")
fig_hist.update_layout(
    xaxis_title='全國錄取分數百分位 (0–100)',
    yaxis_title='校系數',
    height=350,
)
st.plotly_chart(fig_hist, use_container_width=True)

st.divider()

# ── 跟其他學門比較 ──
st.markdown('### 🆚 跟其他學門比較')
fig_compare = go.Figure()
fig_compare.add_trace(go.Scatter(
    x=agg['median_pr_pct'], y=agg['P50'],
    mode='markers+text',
    text=agg['short_name'],
    textposition='top center',
    textfont=dict(size=9, color='lightgray'),
    marker=dict(size=10, color='lightgray', line=dict(width=0.5)),
    name='其他學門',
    hovertext=agg['學門'],
    hoverinfo='text',
))
fig_compare.add_trace(go.Scatter(
    x=[xm_row['median_pr_pct']], y=[xm_row['P50']],
    mode='markers+text',
    text=[xm_row['short_name']],
    textposition='top center',
    textfont=dict(size=12, color='red'),
    marker=dict(size=24, color='red', symbol='star', line=dict(width=2, color='gold')),
    name=xuemen_sel,
    hovertext=xuemen_sel,
    hoverinfo='text',
))
fig_compare.update_layout(
    xaxis_title='中位錄取分數百分位',
    yaxis_title='P50 薪資 (元/月)',
    yaxis=dict(tickformat=','),
    height=480,
    showlegend=False,
)
st.plotly_chart(fig_compare, use_container_width=True)
