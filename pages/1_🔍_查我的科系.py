"""
查我的科系：使用者輸入學校 + 系名（或直接從下拉選），
顯示該校系對應的學門 / P25-P50-P75 / 殘差 / 在散佈圖的位置。
"""
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

DATA = Path(__file__).parent.parent / 'data'

st.set_page_config(page_title='查我的科系', page_icon='🔍', layout='wide')


@st.cache_data
def load_uac():
    return pd.read_csv(DATA / 'uac_with_xuemen.csv',
                       dtype={'系組代碼': str})


@st.cache_data
def load_final_v2():
    return pd.read_csv(DATA / 'final_dataset_v2.csv')


uac = load_uac()
agg = load_final_v2()

# 只保留已對應到學門、且學門在 final_v2 內的校系
uac_valid = uac[
    uac['學門'].notna() &
    uac['學門'].isin(agg['學門'])
].copy()

st.title('🔍 查我的科系所在位置')
st.markdown('''
輸入你的學校和系名，自動找出對應的「學門大類」與該學門的薪資 / 殘差 / 位置資訊。
''')

# ── Selectors ──
col1, col2 = st.columns([1, 1.4])
with col1:
    schools = sorted(uac_valid['校名'].unique())
    school_sel = st.selectbox(
        '🏫 選擇學校',
        options=['(請選擇)'] + schools,
        index=0,
    )

with col2:
    if school_sel != '(請選擇)':
        depts_in_school = uac_valid[uac_valid['校名'] == school_sel]['系組名'].unique()
        dept_sel = st.selectbox(
            f'📚 選擇 {school_sel} 的系組',
            options=['(請選擇)'] + sorted(depts_in_school.tolist()),
        )
    else:
        dept_sel = '(請選擇)'
        st.info('先選學校，會列出該校所有系組。')

# ── 查詢結果 ──
if school_sel != '(請選擇)' and dept_sel != '(請選擇)':
    row = uac_valid[
        (uac_valid['校名'] == school_sel) &
        (uac_valid['系組名'] == dept_sel)
    ].iloc[0]
    xuemen = row['學門']
    xm_row = agg[agg['學門'] == xuemen].iloc[0]

    st.divider()
    st.markdown(f'### 🎯 結果：**{school_sel} {dept_sel}**')
    st.markdown(f'對應的學門大類是 **{xuemen}**（三分群：{xm_row["三分群"]}）')

    # Stats
    c1, c2, c3, c4 = st.columns(4)
    c1.metric('我的校系錄取分數', f"{row['錄取分數']:.0f}",
              help='114 學年大考分發加權錄取分數')
    c2.metric('我的校系達成率', f"{row['達成率']:.1f}%",
              help='錄取分數 / 加權滿分')
    c3.metric('我的校系全國百分位', f"{row['錄取分數百分位']:.1f}",
              help=f'在全國 1772 個校系中的相對位置')
    c4.metric(f'學門中位 PR', f"{xm_row['median_pr_pct']:.1f}",
              delta=f"{row['錄取分數百分位'] - xm_row['median_pr_pct']:+.1f} vs 學門中位",
              help='該學門所有校系的中位錄取分數百分位')

    st.markdown('---')
    st.markdown(f'### 💰 {xuemen} 的薪資分布（勞動部 114/07）')
    s1, s2, s3, s4 = st.columns(4)
    s1.metric('P25 (低標)', f"{xm_row['P25']:,} 元")
    s2.metric('P50 (中位數)', f"{xm_row['P50']:,} 元")
    s3.metric('P75 (高標)', f"{xm_row['P75']:,} 元")
    s4.metric('風險指標', f"{xm_row['風險指標']:.3f}",
              help='(P75-P25)/P50：越大薪資離散度越高、贏家通吃；越小薪資越集中')

    # 殘差解讀
    resid = xm_row['residual_P50']
    if resid > 3000:
        verdict = f'🔵 **被低估** (殘差 {resid:+,} 元)：同 PR 應得 {xm_row["P50_pred"]:,}，但實際 {xm_row["P50"]:,}，多賺 {resid:,}'
        color = 'success'
    elif resid < -3000:
        verdict = f'🔴 **被高估** (殘差 {resid:+,} 元)：同 PR 應得 {xm_row["P50_pred"]:,}，但實際 {xm_row["P50"]:,}，少 {-resid:,}'
        color = 'warning'
    else:
        verdict = f'⚪ **大致符合** (殘差 {resid:+,} 元)：薪資跟錄取分數的關係大致符合全國趨勢'
        color = 'info'

    if color == 'success':
        st.success(verdict)
    elif color == 'warning':
        st.warning(verdict)
    else:
        st.info(verdict)

    # ── 在散佈圖中標出 ──
    st.markdown(f'### 📍 你的學門在散佈圖上的位置')

    palette = {'應用 STEM': '#1f77b4', '基礎 STEM': '#2ca02c', '人文社科': '#d62728'}
    fig = go.Figure()

    for g, sub in agg.groupby('三分群'):
        is_my = sub['學門'] == xuemen
        fig.add_trace(go.Scatter(
            x=sub['median_pr_pct'], y=sub['P50'],
            mode='markers+text',
            text=sub['short_name'],
            textposition='top center',
            textfont=dict(size=10),
            marker=dict(
                size=[28 if my else 12 for my in is_my],
                color=palette[g],
                line=dict(
                    width=[3 if my else 0.5 for my in is_my],
                    color=['gold' if my else 'white' for my in is_my],
                ),
                symbol=['star' if my else 'circle' for my in is_my],
            ),
            name=g,
            hovertext=sub['學門'],
            hoverinfo='text',
        ))

    # 標出自己的校系（不是學門中位）位置
    fig.add_trace(go.Scatter(
        x=[row['錄取分數百分位']],
        y=[xm_row['P50']],
        mode='markers',
        marker=dict(size=18, color='red', symbol='cross-thin-open',
                    line=dict(width=3, color='red')),
        name=f'你的校系 ({row["錄取分數百分位"]:.0f}, 學門 P50)',
        hovertext=f'{school_sel} {dept_sel}<br>校系 PR 百分位：{row["錄取分數百分位"]:.1f}',
        hoverinfo='text',
    ))

    fig.update_layout(
        xaxis_title='中位錄取分數百分位',
        yaxis_title='P50 中位薪資 (元/月)',
        yaxis=dict(tickformat=','),
        height=560,
        legend=dict(orientation='h', yanchor='bottom', y=1.02),
    )
    st.plotly_chart(fig, use_container_width=True)

    st.caption(
        '⭐ 金色星星 = 你的學門大類在 25 學門裡的位置；🔴 紅色十字 = 你的校系錄取 PR 百分位'
    )
