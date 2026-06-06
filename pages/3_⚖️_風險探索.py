"""
風險探索：用 (P75-P25)/P50 看每個學門的薪資離散度，
搭配 P50 雙軸視覺化「贏家通吃」vs「保守型」學門。
"""
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

DATA = Path(__file__).parent.parent / 'data'

st.set_page_config(page_title='風險探索', page_icon='⚖️', layout='wide')


@st.cache_data
def load():
    return pd.read_csv(DATA / 'final_dataset_v2.csv')


df = load()

st.title('⚖️ 風險探索：薪資的天花板與地板')
st.markdown('''
薪資中位數 (P50) 只說了一半的故事。**風險指標 = (P75 − P25) / P50** 量化「同學門內薪資的離散程度」：
- **風險指標越大** = 同學門內薪資差距越懸殊（贏家通吃）
- **風險指標越小** = 同學門內薪資集中（穩定保守）

例如「**法律**」風險 0.534 — 律師月入十幾萬，但法務助理可能 35k；
「**藝術**」風險 0.309 — 多數人都落在 30–40k 區間。
''')

# ── 主視圖：風險指標 vs P50 ──
palette = {'應用 STEM': '#1f77b4', '基礎 STEM': '#2ca02c', '人文社科': '#d62728'}

fig = go.Figure()
for g, sub in df.groupby('三分群'):
    fig.add_trace(go.Scatter(
        x=sub['P50'], y=sub['風險指標'],
        mode='markers+text',
        text=sub['short_name'],
        textposition='top center',
        textfont=dict(size=10),
        marker=dict(
            size=18,
            color=palette[g],
            line=dict(width=1, color='white'),
        ),
        name=g,
        hovertext=sub.apply(
            lambda r: (
                f"<b>{r['學門']}</b><br>"
                f"P25/P50/P75: {r['P25']:,}/{r['P50']:,}/{r['P75']:,} 元<br>"
                f"風險指標: {r['風險指標']:.3f}"),
            axis=1),
        hoverinfo='text',
    ))

# 四象限分割線（中位數）
mid_p50 = df['P50'].median()
mid_risk = df['風險指標'].median()
fig.add_vline(x=mid_p50, line_dash='dot', line_color='gray',
              annotation_text=f'P50 中位 {int(mid_p50):,}')
fig.add_hline(y=mid_risk, line_dash='dot', line_color='gray',
              annotation_text=f'風險中位 {mid_risk:.3f}')

# 象限標籤
xrange = df['P50'].max() - df['P50'].min()
yrange = df['風險指標'].max() - df['風險指標'].min()
fig.add_annotation(x=df['P50'].max() - xrange * 0.05,
                   y=df['風險指標'].max() - yrange * 0.02,
                   text='💰📈 <b>高薪・高分化</b><br>(贏家通吃)',
                   showarrow=False, font=dict(size=11, color='#1f77b4'),
                   align='right')
fig.add_annotation(x=df['P50'].min() + xrange * 0.05,
                   y=df['風險指標'].max() - yrange * 0.02,
                   text='💸📈 <b>低薪・高分化</b>',
                   showarrow=False, font=dict(size=11, color='#888'),
                   align='left')
fig.add_annotation(x=df['P50'].max() - xrange * 0.05,
                   y=df['風險指標'].min() + yrange * 0.02,
                   text='💰📊 <b>高薪・穩定</b>',
                   showarrow=False, font=dict(size=11, color='#2ca02c'),
                   align='right')
fig.add_annotation(x=df['P50'].min() + xrange * 0.05,
                   y=df['風險指標'].min() + yrange * 0.02,
                   text='💸📊 <b>低薪・穩定</b><br>(保守型)',
                   showarrow=False, font=dict(size=11, color='#d62728'),
                   align='left')

fig.update_layout(
    xaxis_title='P50 中位薪資 (元/月)',
    yaxis_title='風險指標 (P75 − P25) / P50',
    xaxis=dict(tickformat=','),
    height=620,
    legend=dict(orientation='h', yanchor='bottom', y=1.02),
)
st.plotly_chart(fig, use_container_width=True)


st.divider()
st.markdown('### 📋 風險指標排名表')

ranked = df.sort_values('風險指標', ascending=False)[
    ['short_name', '三分群', 'P25', 'P50', 'P75', '風險指標']].copy()
ranked.columns = ['學門', '三分群', 'P25', 'P50', 'P75', '風險指標']
ranked['P25'] = ranked['P25'].apply(lambda v: f'{int(v):,}')
ranked['P50'] = ranked['P50'].apply(lambda v: f'{int(v):,}')
ranked['P75'] = ranked['P75'].apply(lambda v: f'{int(v):,}')
ranked['風險指標'] = ranked['風險指標'].apply(lambda v: f'{v:.3f}')

st.dataframe(ranked, hide_index=True, use_container_width=True)

st.info('''
**Top 3 高分化學門**（贏家通吃明顯）：
1. 工程及工程業 (0.627) — 半導體 / IC 業精英 vs 一般工程師差距大
2. 物理、化學及地球科學 (0.615) — 半導體研發 vs 學術圈底層
3. 資訊通訊科技 (0.605) — 軟體大廠 vs 一般 IT 落差顯著

**Bottom 3 穩定學門**（保守型）：
1. 社會福利 (0.275) — 薪資範圍最窄
2. 藝術 (0.309)
3. 新聞學及圖書資訊 (0.315)
''')
