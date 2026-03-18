# ============================================================
# app.py — Streamlit UI
# ============================================================
# Run: streamlit run app.py

import os
import streamlit as st

os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
os.environ["TF_CPP_MIN_LOG_LEVEL"]  = "3"


from config              import SUGGESTED_REPOS
from graph.workflow      import analyse_repo
from ui.styles           import load_css
from ui.components       import (
    hero, repo_header, stats_row, verdict_badge,
    report_box, explainer_card, empty_state, card_open, card_close,
)

st.set_page_config(
    page_title="GitHub Repo Health Monitor",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed",
)

load_css()

# ── Session state
for key, default in [("result", None), ("query", "")]:
    if key not in st.session_state:
        st.session_state[key] = default

# ── Hero
hero()

# ── Layout
col_left, col_right = st.columns([1, 1.3], gap="large")

with col_left:
    card_open("🔍 Analyse Any Public Repo")

    st.html("<div style='color:#475569;font-size:.75rem;margin-bottom:8px'>Quick examples:</div>")
    qcols = st.columns(2)
    for i, repo in enumerate(SUGGESTED_REPOS[:4]):
        with qcols[i % 2]:
            if st.button(repo, key=f"q_{i}", use_container_width=True):
                st.session_state.query = repo
                st.session_state.auto_run = True
                st.rerun()

    st.html("<div style='height:8px'></div>")
    query = st.text_input(
        "repo",
        value=st.session_state.query,
        placeholder="e.g. langchain-ai/langchain or full GitHub URL",
        label_visibility="collapsed",
        key="query_input",
    )
    analyse_btn = st.button("🔍 Analyse Repo", use_container_width=True)
    card_close()

    card_open("🤖 Agent Pipeline")
    st.html("""
    <div style='display:flex;flex-direction:column;gap:8px'>
      <div style='display:flex;align-items:center;gap:10px'>
        <span style='color:#3b82f6;font-size:1rem'>1</span>
        <span style='color:#94a3b8;font-size:.82rem'>🔴 <b>Repo Fetcher</b> — stars, commits, issues, releases</span>
      </div>
      <div style='display:flex;align-items:center;gap:10px'>
        <span style='color:#3b82f6;font-size:1rem'>2</span>
        <span style='color:#94a3b8;font-size:.82rem'>📊 <b>Activity Analyst</b> + 💬 <b>Community Analyst</b> — parallel</span>
      </div>
      <div style='display:flex;align-items:center;gap:10px'>
        <span style='color:#3b82f6;font-size:1rem'>3</span>
        <span style='color:#94a3b8;font-size:.82rem'>📝 <b>Report Writer</b> — final verdict + next steps</span>
      </div>
      <div style='display:flex;align-items:center;gap:10px'>
        <span style='color:#3b82f6;font-size:1rem'>4</span>
        <span style='color:#94a3b8;font-size:.82rem'>📈 <b>Chart Generator</b> — commit trends, health radar</span>
      </div>
    </div>
    <div style='color:#334155;font-size:.74rem;margin-top:10px'>
      Powered by LangGraph · Groq · GitHub Public API
    </div>
    """)
    card_close()

with col_right:
    trigger = analyse_btn or st.session_state.get("auto_run", False)
    if trigger:
        st.session_state.auto_run = False
        q = query.strip()
        if not q:
            st.warning("Please enter a repository name or URL.")
        else:
            st.session_state.query = q
            with st.spinner("🤖 Fetching repo data and running analysis..."):
                result = analyse_repo(q)
                st.session_state.result = result

    if st.session_state.result:
        result = st.session_state.result

        if result.get("status") == "error":
            st.error(result.get("report", "Analysis failed."))
        else:
            repo_data      = result.get("repo_data", {})
            activity_data  = result.get("activity_data", {})
            community_data = result.get("community_data", {})

            repo_header(repo_data)
            stats_row(repo_data)
            st.html("<div style='height:12px'></div>")

            verdict_badge(
                result.get("verdict", "MONITOR"),
                activity_data.get("signal", "UNKNOWN"),
                community_data.get("sentiment_label", "UNKNOWN"),
            )

            # ── Repo Explainer — show right after verdict
            explainer_data = result.get("explainer_data", {})
            #if explainer_data.get("success"):
            #    explainer_card(explainer_data)

            # Scroll-to-charts indicator
            if result.get("charts"):
                st.html("""
                <a href="#charts" style="text-decoration:none">
                  <div style="display:flex;align-items:center;justify-content:center;gap:10px;
                    background:linear-gradient(135deg,#0c1420,#111d2e);border:1px solid #3b82f644;
                    border-radius:12px;padding:12px 20px;margin:14px 0;cursor:pointer">
                    <span style="color:#3b82f6;font-size:.85rem;font-weight:600">📈 Interactive Charts Below</span>
                    <span style="animation:bounce 1.2s infinite;display:inline-block">↓</span>
                  </div>
                </a>
                """)

            st.html("<div style='height:16px'></div>")
            tab_report, tab_activity, tab_community, tab_explain = st.tabs([
                "📋 Full Report", "📊 Activity Analysis", "💬 Community Analysis", "🧠 Deep Explanation"
            ])
            with tab_report:
                report_box(result.get("report", "No report."))
                st.download_button(
                    "⬇️ Download Report",
                    data=result.get("report", "").encode(),
                    file_name=f"{repo_data.get('repo','repo')}_health.txt",
                    mime="text/plain",
                )
            with tab_activity:
                report_box(activity_data.get("analysis", "No analysis."))
            with tab_community:
                report_box(community_data.get("sentiment", "No sentiment data."))
            with tab_explain:
                explainer_data = result.get("explainer_data", {})
                report_box(explainer_data.get("explanation", "No explanation available."))
    else:
        empty_state()

# ── Charts: full width below columns
if st.session_state.result and st.session_state.result.get("status") != "error":
    charts = st.session_state.result.get("charts", {})
    if charts:
        st.markdown("---")
        st.html('<h3 id="charts">📈 Interactive Charts</h3>')
        tab_gauge, tab_commits, tab_radar, tab_issues = st.tabs([
            "🎯 Health Score", "📅 Commit History", "🕸️ Health Radar", "🐛 Issues"
        ])
        with tab_gauge:
            if "gauge" in charts:
                st.plotly_chart(charts["gauge"], use_container_width=True)
        with tab_commits:
            if "commits" in charts:
                st.plotly_chart(charts["commits"], use_container_width=True)
            else:
                st.info("Not enough commit data")
        with tab_radar:
            if "radar" in charts:
                st.plotly_chart(charts["radar"], use_container_width=True)
        with tab_issues:
            if "issues" in charts:
                st.plotly_chart(charts["issues"], use_container_width=True)