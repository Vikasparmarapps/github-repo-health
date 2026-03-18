# ============================================================
# ui/components.py — Reusable UI components
# ============================================================

import streamlit as st
from config import APP_TITLE, APP_SUBTITLE


def hero():
    st.html(f"""
    <div class="hero">
      <h1>{APP_TITLE}</h1>
      <p>{APP_SUBTITLE}</p>
    </div>
    """)


def repo_header(repo_data: dict):
    """Main repo info card."""
    meta    = repo_data.get("meta", {})
    health  = repo_data.get("health", {})
    score   = health.get("score", 0)
    label   = health.get("label", "")

    score_color = (
        "#22c55e" if score >= 75 else
        "#F0B90B" if score >= 50 else
        "#f97316" if score >= 30 else
        "#ef4444"
    )

    archived_badge = "<span class='archived-badge'>ARCHIVED</span>" if meta.get('archived') else ""

    st.html(f"""
    <div class="card">
      <div class="card-title">📦 Repository Overview</div>
      <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:12px">
        <div>
          <div class="price-big">
            <a href="{meta.get('url','')}" target="_blank"
               style="color:#f1f5f9;text-decoration:none">{meta.get('full_name','')}</a>
          </div>
          <div class="coin-name" style="margin-top:6px">{meta.get('description','No description')}</div>
          <div style="margin-top:8px;display:flex;gap:8px;flex-wrap:wrap">
            <span class="lang-badge">{meta.get('language','Unknown')}</span>
            <span class="lang-badge">{meta.get('license','No license')}</span>
            {archived_badge}
          </div>
        </div>
        <div style="text-align:center;min-width:100px">
          <div style="font-size:2.2rem;font-weight:700;color:{score_color};font-family:'JetBrains Mono',monospace">{score}</div>
          <div style="font-size:.75rem;color:{score_color};font-weight:600">{label}</div>
          <div style="font-size:.65rem;color:#475569;margin-top:2px">Health Score</div>
        </div>
      </div>
    </div>
    """)


def stats_row(repo_data: dict):
    """Stars / forks / open issues / last push stats."""
    meta    = repo_data.get("meta", {})
    commits = repo_data.get("commits", {})

    days = meta.get("days_since_push", 9999)
    if days == 0:
        push_str = "Today"
    elif days == 1:
        push_str = "Yesterday"
    elif days < 30:
        push_str = f"{days}d ago"
    elif days < 365:
        push_str = f"{days//30}mo ago"
    else:
        push_str = f"{days//365}y ago"

    trend = commits.get("trend_pct", 0)
    trend_color = "#22c55e" if trend >= 0 else "#ef4444"
    trend_str = f"{trend:+.0f}%"

    c1, c2, c3, c4 = st.columns(4)
    for col, num, lbl in [
        (c1, f"⭐ {repo_data.get('stars_fmt','0')}", "Stars"),
        (c2, f"🍴 {repo_data.get('forks_fmt','0')}", "Forks"),
        (c3, f"🐛 {repo_data.get('issues_fmt','0')}", "Open Issues"),
        (c4, push_str, "Last Push"),
    ]:
        with col:
            st.html(
                f'<div class="stat-box"><div class="stat-num">{num}</div>'
                f'<div class="stat-label">{lbl}</div></div>'
            )


def verdict_badge(verdict: str, activity_signal: str, community_signal: str):
    configs = {
        "ADOPT":            ("verdict-adopt",   "✅ ADOPT"),
        "USE WITH CAUTION": ("verdict-caution", "⚠️ USE WITH CAUTION"),
        "MONITOR":          ("verdict-monitor", "👁️ MONITOR"),
        "REPLACE":          ("verdict-replace", "🚨 REPLACE"),
    }
    cls, label = configs.get(verdict, ("verdict-monitor", verdict))
    st.html(f"""
    <div style="display:flex;gap:10px;flex-wrap:wrap;margin-bottom:12px">
      <div class="verdict-badge {cls}">{label}</div>
      <div class="signal-badge">Activity: {activity_signal}</div>
      <div class="signal-badge">Community: {community_signal}</div>
    </div>
    """)


def report_box(text: str):
    import re
    text = re.sub(r'## (.+)', r'<h2>\1</h2>', text)
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = text.replace('\n', '<br>')
    st.html(f'<div class="report-box">{text}</div>')


def empty_state():
    st.html("""
    <div style='text-align:center;padding:60px 20px;color:#94a3b8'>
      <div style='font-size:3rem;margin-bottom:12px'>🔍</div>
      <div style='font-size:1rem;font-weight:600'>Enter any public GitHub repository</div>
      <div style='font-size:.82rem;color:#475569;margin-top:6px'>
        e.g. "langchain-ai/langchain" or "https://github.com/streamlit/streamlit"
      </div>
    </div>
    """)


def explainer_card(explainer_data: dict):
    """What is this repo — plain English explanation."""
    topics = explainer_data.get("topics", [])
    language = explainer_data.get("language", "")

    topic_pills = "".join(
        f'<span class="lang-badge">{t}</span> '
        for t in topics[:6]
    )

    st.html(f"""
    <div class="card">
      <div class="card-title">🧠 What Is This Repo?</div>
      <div style="display:flex;gap:6px;flex-wrap:wrap;margin-bottom:12px">
        {"<span class='lang-badge'>" + language + "</span>" if language else ""}
        {topic_pills}
      </div>
    </div>
    """)

    report_box(explainer_data.get("explanation", "No explanation available."))


def card_open(title=""):
    title_html = f'<div class="card-title">{title}</div>' if title else ''
    st.html(f'<div class="card">{title_html}')


def card_close():
    st.html('</div>')