"""Streamlit 双向、可解释简历—岗位匹配看板。"""

from __future__ import annotations

import html
import io
from pathlib import Path

import pandas as pd
import streamlit as st

from src.data_io import clean_jobs, clean_resumes
from src.matcher import ResumeJobMatcher


ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"

st.set_page_config(
    page_title="AI 人岗智能匹配",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="auto",
)


st.markdown(
    """
    <style>
    :root {
        --navy: #071f3d;
        --navy-2: #12345a;
        --blue: #2457e6;
        --blue-soft: #eef3ff;
        --ink: #12233f;
        --muted: #66748a;
        --line: #dce3ee;
        --teal: #0f9f87;
        --amber: #d88613;
        --surface: #ffffff;
        --canvas: #f6f8fb;
    }
    [data-testid="stAppViewContainer"] { background: var(--canvas); }
    [data-testid="stHeader"] { background: transparent; }
    [data-testid="stSidebar"] { background: var(--navy); border-right: 0; }
    [data-testid="stSidebar"] * { color: #f8fbff; }
    [data-testid="stSidebar"] label, [data-testid="stSidebar"] p {
        color: #d5dfec !important;
    }
    [data-testid="stSidebar"] [data-baseweb="select"] * { color: #14233a !important; }
    [data-testid="stSidebar"] input { color: #14233a !important; }
    [data-testid="stSidebar"] .stSlider [data-testid="stThumbValue"] { color: #fff !important; }
    [data-testid="stSidebar"] hr { border-color: rgba(255,255,255,.14); }
    .block-container { max-width: 1480px; padding: 1.15rem 2.0rem 2.5rem; }
    h1, h2, h3 { color: var(--ink); letter-spacing: -0.02em; }
    h1 { font-size: 2rem !important; margin: 0 !important; }
    h2 { font-size: 1.3rem !important; }
    h3 { font-size: 1.0rem !important; }
    .sidebar-brand {
        display:flex; align-items:center; gap:.72rem; padding:.4rem .1rem 1.15rem;
        border-bottom:1px solid rgba(255,255,255,.14); margin-bottom:1rem;
    }
    .brand-mark {
        width:38px; height:38px; border-radius:10px; background:#2d62ef; color:#fff;
        display:grid; place-items:center; font-weight:800; font-size:15px;
    }
    .brand-title { color:#fff; font-weight:750; line-height:1.1; }
    .brand-sub { color:#9fb0c5; font-size:11px; margin-top:4px; }
    .eyebrow { color:var(--blue); font-weight:750; font-size:.76rem; letter-spacing:.11em; text-transform:uppercase; }
    .subtitle { color:var(--muted); margin:.2rem 0 1.05rem; font-size:.92rem; }
    .status-row { display:flex; gap:.45rem; flex-wrap:wrap; margin:.55rem 0 .95rem; }
    .status-pill {
        display:inline-flex; align-items:center; gap:.35rem; border:1px solid var(--line);
        border-radius:999px; padding:.28rem .58rem; background:#fff; color:var(--muted); font-size:.76rem;
    }
    .status-dot { width:7px; height:7px; border-radius:50%; background:var(--teal); }
    .profile-card, .leader-card, .reason-card {
        background:var(--surface); border:1px solid var(--line); border-radius:12px; padding:1rem 1.05rem;
    }
    .profile-card { min-height:142px; }
    .profile-id { color:var(--blue); font-size:.75rem; font-weight:750; letter-spacing:.06em; }
    .profile-name { color:var(--ink); font-size:1.16rem; font-weight:760; margin:.16rem 0 .2rem; }
    .profile-meta { color:var(--muted); font-size:.83rem; line-height:1.55; }
    .leader-card { border-top:3px solid var(--blue); min-height:142px; }
    .leader-label { color:var(--muted); font-size:.75rem; font-weight:700; }
    .leader-title { color:var(--ink); font-weight:760; margin:.24rem 0 .05rem; }
    .leader-company { color:var(--muted); font-size:.82rem; }
    .leader-score { color:var(--blue); font-size:1.75rem; font-weight:800; margin-top:.32rem; }
    .leader-score span { color:var(--muted); font-size:.76rem; font-weight:600; }
    .chip-wrap { display:flex; flex-wrap:wrap; gap:.38rem; margin:.42rem 0 .72rem; }
    .chip { border-radius:999px; padding:.25rem .55rem; font-size:.76rem; font-weight:650; }
    .chip-ok { background:#e8f7f3; color:#087967; border:1px solid #bee9de; }
    .chip-miss { background:#fff5e6; color:#a55d05; border:1px solid #f3d7ad; }
    .reason-card { background:#f8faff; border-color:#cfdaf5; color:#374969; font-size:.86rem; line-height:1.55; }
    .reason-title { color:#244fb7; font-weight:760; margin-bottom:.22rem; }
    [data-testid="stMetric"] {
        background:#fff; border:1px solid var(--line); border-radius:10px; padding:.7rem .8rem;
    }
    [data-testid="stMetricLabel"] { color:var(--muted); }
    [data-testid="stMetricValue"] { color:var(--ink); }
    div[data-testid="stRadio"] > div { gap:.35rem; }
    div[data-testid="stRadio"] label {
        background:#fff; border:1px solid var(--line); border-radius:9px; padding:.3rem .7rem;
    }
    .section-label { color:var(--ink); font-size:.92rem; font-weight:760; margin:.7rem 0 .35rem; }
    .sidebar-note {
        margin-top:1rem; padding:.72rem; border:1px solid rgba(255,255,255,.14);
        border-radius:10px; color:#aabbd0; font-size:.72rem; line-height:1.5;
    }
    .footer-note { color:var(--muted); font-size:.74rem; padding-top:.5rem; }
    @media (max-width: 720px) {
        .block-container { padding:.85rem .9rem 1.8rem; }
        h1 { font-size:1.55rem !important; }
        .profile-card, .leader-card { min-height:auto; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data(show_spinner="正在训练 TF-IDF 与 Word2Vec 并计算匹配分…")
def compute_results(
    resume_bytes: bytes,
    job_bytes: bytes,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, int]:
    resumes = clean_resumes(pd.read_csv(io.BytesIO(resume_bytes), encoding="utf-8-sig"))
    jobs = clean_jobs(pd.read_csv(io.BytesIO(job_bytes), encoding="utf-8-sig"))
    matcher = ResumeJobMatcher(resumes, jobs)
    results = matcher.match_all()
    return results, matcher.resumes, matcher.jobs, matcher.vocabulary_size


def _safe(value: object) -> str:
    return html.escape(str(value))


def _chips(raw: object, css_class: str, empty_text: str) -> str:
    items = [item for item in str(raw or "").split(";") if item]
    if not items:
        items = [empty_text]
    return "".join(
        f'<span class="chip {css_class}">{_safe(item)}</span>' for item in items
    )


def render_dimension_chart(row: pd.Series) -> None:
    chart = pd.DataFrame(
        {
            "维度": ["技能", "TF-IDF", "Word2Vec", "学历", "经验", "城市", "证书"],
            "得分": [
                row["skill_score"],
                row["tfidf_score"],
                row["word2vec_score"],
                row["education_score"],
                row["experience_score"],
                row["city_score"],
                row["certificate_score"],
            ],
        }
    )
    st.vega_lite_chart(
        chart,
        {
            "height": 245,
            "mark": {"type": "bar", "cornerRadiusEnd": 5, "color": "#2457e6"},
            "encoding": {
                "y": {
                    "field": "维度",
                    "type": "nominal",
                    "sort": None,
                    "axis": {"title": None, "labelColor": "#4f5f76"},
                },
                "x": {
                    "field": "得分",
                    "type": "quantitative",
                    "scale": {"domain": [0, 100]},
                    "axis": {"title": None, "gridColor": "#e9edf4", "labelColor": "#738096"},
                },
                "tooltip": [
                    {"field": "维度", "type": "nominal"},
                    {"field": "得分", "type": "quantitative", "format": ".1f"},
                ],
            },
            "config": {"view": {"stroke": None}, "background": "#ffffff"},
        },
        use_container_width=True,
    )


def render_metrics(row: pd.Series) -> None:
    columns = st.columns(4)
    labels = ["综合匹配", "技能覆盖", "TF-IDF", "Word2Vec"]
    keys = ["total_score", "skill_score", "tfidf_score", "word2vec_score"]
    for column, label, key in zip(columns, labels, keys):
        column.metric(label, f"{float(row[key]):.1f}")


def render_explanation(row: pd.Series) -> None:
    st.markdown('<div class="section-label">匹配依据</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="chip-wrap">'
        + _chips(row["matched_skills"], "chip-ok", "暂无命中技能")
        + "</div>",
        unsafe_allow_html=True,
    )
    if str(row["missing_skills"]):
        st.markdown(
            '<div class="chip-wrap">'
            + _chips(row["missing_skills"], "chip-miss", "无待提升技能")
            + "</div>",
            unsafe_allow_html=True,
        )
    st.markdown(
        f'<div class="reason-card"><div class="reason-title">为什么推荐</div>{_safe(row["reason"])}</div>',
        unsafe_allow_html=True,
    )


with st.sidebar:
    st.markdown(
        """
        <div class="sidebar-brand">
          <div class="brand-mark">AI</div>
          <div><div class="brand-title">人岗智能匹配</div><div class="brand-sub">RESUME × JOB</div></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.caption("数据源")
    with st.expander("上传自定义 CSV", expanded=False):
        uploaded_resumes = st.file_uploader("简历数据", type=["csv"], key="resume_upload")
        uploaded_jobs = st.file_uploader("岗位数据", type=["csv"], key="job_upload")
        st.caption("未上传的文件自动使用项目示例数据。")

resume_bytes = (
    uploaded_resumes.getvalue()
    if uploaded_resumes is not None
    else (DATA_DIR / "resumes.csv").read_bytes()
)
job_bytes = (
    uploaded_jobs.getvalue()
    if uploaded_jobs is not None
    else (DATA_DIR / "jobs.csv").read_bytes()
)

try:
    results, resumes, jobs, vocabulary_size = compute_results(resume_bytes, job_bytes)
except Exception as exc:
    st.error(f"数据读取或匹配失败：{exc}")
    st.stop()

with st.sidebar:
    st.caption("筛选与排序")
    top_n = st.slider("显示 Top N", 1, min(10, max(len(resumes), len(jobs))), 5)
    min_score = st.slider("最低综合分", 0, 100, 0, 5)
    st.markdown(
        f"""
        <div class="sidebar-note">
          <b>本地模型已就绪</b><br>
          {len(resumes)} 份简历 · {len(jobs)} 个岗位<br>
          Word2Vec 词表 {vocabulary_size} 个词<br>
          计算结果不会离开当前 Docker 环境
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown('<div class="eyebrow">Talent Intelligence Workspace</div>', unsafe_allow_html=True)
st.title("AI 人岗智能匹配")
st.markdown(
    '<div class="subtitle">融合词袋、TF-IDF、Word2Vec 与业务规则，提供双向排名和逐项解释。</div>',
    unsafe_allow_html=True,
)
st.markdown(
    f"""
    <div class="status-row">
      <span class="status-pill"><span class="status-dot"></span>模型在线</span>
      <span class="status-pill">本地 Docker</span>
      <span class="status-pill">{len(results)} 组配对已评分</span>
    </div>
    """,
    unsafe_allow_html=True,
)

perspective = st.radio(
    "匹配视角",
    ["学生找岗位", "岗位找人才"],
    horizontal=True,
    label_visibility="collapsed",
)

if perspective == "学生找岗位":
    resume_labels = {
        f"{row.resume_id} · {row.name} — {row.major}": row.resume_id
        for row in resumes.itertuples()
    }
    control_a, control_b = st.columns([1.7, 1])
    selected_label = control_a.selectbox("选择学生", list(resume_labels))
    available_cities = ["全部"] + sorted(jobs["city"].dropna().unique().tolist())
    selected_city = control_b.selectbox("岗位城市", available_cities)
    selected_id = resume_labels[selected_label]
    profile = resumes.loc[resumes["resume_id"] == selected_id].iloc[0]
    view = results.loc[results["resume_id"] == selected_id].copy()
    if selected_city != "全部":
        view = view.loc[view["job_city"] == selected_city]
    view = view.loc[view["total_score"] >= min_score].nlargest(top_n, "total_score")

    if view.empty:
        st.warning("当前筛选条件下没有岗位，请降低最低分或切换城市。")
        st.stop()
    leader = view.iloc[0]
    left, right = st.columns([1.65, 1])
    left.markdown(
        f"""
        <div class="profile-card">
          <div class="profile-id">候选人 · {_safe(profile['resume_id'])}</div>
          <div class="profile-name">{_safe(profile['name'])}</div>
          <div class="profile-meta">{_safe(profile['education'])} · {_safe(profile['major'])}<br>
          {_safe(profile['city'])} · {_safe(profile['experience_years'])} 年经验 · 期望薪资 ¥{float(profile['expected_salary']):,.0f}<br>
          {_safe(profile['skills'])}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    right.markdown(
        f"""
        <div class="leader-card">
          <div class="leader-label">TOP 1 推荐岗位</div>
          <div class="leader-title">{_safe(leader['job_title'])}</div>
          <div class="leader-company">{_safe(leader['company'])} · {_safe(leader['job_city'])}</div>
          <div class="leader-score">{float(leader['total_score']):.1f}<span> / 100</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    render_metrics(leader)
    explain_col, chart_col = st.columns([1.15, 1])
    with explain_col:
        render_explanation(leader)
    with chart_col:
        st.markdown('<div class="section-label">七维评分</div>', unsafe_allow_html=True)
        render_dimension_chart(leader)

    st.markdown('<div class="section-label">岗位推荐列表</div>', unsafe_allow_html=True)
    display = view[
        ["job_title", "company", "job_city", "salary", "total_score", "skill_score", "reason"]
    ].copy()
    display.insert(0, "排名", range(1, len(display) + 1))
    st.dataframe(
        display,
        hide_index=True,
        use_container_width=True,
        column_config={
            "salary": st.column_config.NumberColumn("月薪", format="¥%d"),
            "total_score": st.column_config.ProgressColumn("综合分", min_value=0, max_value=100, format="%.1f"),
            "skill_score": st.column_config.NumberColumn("技能分", format="%.1f"),
            "reason": st.column_config.TextColumn("推荐理由", width="large"),
        },
    )
    st.download_button(
        "下载该学生的推荐结果",
        view.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig"),
        file_name=f"{selected_id}_top_jobs.csv",
        mime="text/csv",
        type="primary",
    )

else:
    job_labels = {
        f"{row.job_id} · {row.job_title} — {row.company}": row.job_id
        for row in jobs.itertuples()
    }
    control_a, control_b = st.columns([1.7, 1])
    selected_label = control_a.selectbox("选择岗位", list(job_labels))
    available_cities = ["全部"] + sorted(resumes["city"].dropna().unique().tolist())
    selected_city = control_b.selectbox("候选人城市", available_cities)
    selected_id = job_labels[selected_label]
    profile = jobs.loc[jobs["job_id"] == selected_id].iloc[0]
    view = results.loc[results["job_id"] == selected_id].copy()
    if selected_city != "全部":
        view = view.loc[view["resume_city"] == selected_city]
    view = view.loc[view["total_score"] >= min_score].nlargest(top_n, "total_score")

    if view.empty:
        st.warning("当前筛选条件下没有候选人，请降低最低分或切换城市。")
        st.stop()
    leader = view.iloc[0]
    left, right = st.columns([1.65, 1])
    left.markdown(
        f"""
        <div class="profile-card">
          <div class="profile-id">招聘岗位 · {_safe(profile['job_id'])}</div>
          <div class="profile-name">{_safe(profile['job_title'])}</div>
          <div class="profile-meta">{_safe(profile['company'])} · {_safe(profile['city'])}<br>
          {_safe(profile['required_education'])}及以上 · {_safe(profile['min_experience_years'])} 年经验 · 月薪 ¥{float(profile['salary']):,.0f}<br>
          {_safe(profile['required_skills'])}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    right.markdown(
        f"""
        <div class="leader-card">
          <div class="leader-label">TOP 1 推荐候选人</div>
          <div class="leader-title">{_safe(leader['student_name'])}</div>
          <div class="leader-company">{_safe(leader['major'])} · {_safe(leader['resume_city'])}</div>
          <div class="leader-score">{float(leader['total_score']):.1f}<span> / 100</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    render_metrics(leader)
    explain_col, chart_col = st.columns([1.15, 1])
    with explain_col:
        render_explanation(leader)
    with chart_col:
        st.markdown('<div class="section-label">七维评分</div>', unsafe_allow_html=True)
        render_dimension_chart(leader)

    st.markdown('<div class="section-label">候选人推荐列表</div>', unsafe_allow_html=True)
    display = view[
        ["student_name", "education", "major", "resume_city", "total_score", "skill_score", "reason"]
    ].copy()
    display.insert(0, "排名", range(1, len(display) + 1))
    st.dataframe(
        display,
        hide_index=True,
        use_container_width=True,
        column_config={
            "total_score": st.column_config.ProgressColumn("综合分", min_value=0, max_value=100, format="%.1f"),
            "skill_score": st.column_config.NumberColumn("技能分", format="%.1f"),
            "reason": st.column_config.TextColumn("推荐理由", width="large"),
        },
    )
    st.download_button(
        "下载该岗位的候选人结果",
        view.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig"),
        file_name=f"{selected_id}_top_candidates.csv",
        mime="text/csv",
        type="primary",
    )

st.markdown(
    '<div class="footer-note">评分公式：技能 30% · TF-IDF 20% · Word2Vec 15% · 学历 15% · 经验 10% · 城市 5% · 证书 5%</div>',
    unsafe_allow_html=True,
)
