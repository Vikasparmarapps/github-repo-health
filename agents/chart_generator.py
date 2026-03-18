# ============================================================
# agents/chart_generator.py — Agent 5: Generate charts
# ============================================================

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np


def generate_commit_chart(weekly: list, repo_name: str) -> go.Figure:
    """52-week commit activity bar chart with rolling average."""
    weeks = list(range(1, len(weekly) + 1))
    rolling = pd.Series(weekly).rolling(4, min_periods=1).mean().tolist()

    # Color bars: recent = brighter
    colors = ["#1e3a5f"] * len(weekly)
    for i in range(max(0, len(weekly)-12), len(weekly)):
        colors[i] = "#2563eb"
    for i in range(max(0, len(weekly)-4), len(weekly)):
        colors[i] = "#F0B90B"

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=weeks, y=weekly,
        name="Commits",
        marker=dict(color=colors),
        hovertemplate="Week %{x}: %{y} commits<extra></extra>"
    ))
    fig.add_trace(go.Scatter(
        x=weeks, y=rolling,
        name="4-week avg",
        line=dict(color="#ef4444", width=2),
        hovertemplate="Avg: %{y:.1f}<extra></extra>"
    ))
    fig.update_layout(
        title=f"<b>{repo_name} — 52-Week Commit Activity</b>",
        height=380, template="plotly_dark",
        hovermode="x unified",
        margin=dict(l=40, r=40, t=50, b=40),
        legend=dict(orientation="h", y=1.1),
        xaxis_title="Week (52 = most recent)",
        yaxis_title="Commits",
    )
    return fig


def generate_health_radar(breakdown: dict, repo_name: str) -> go.Figure:
    """Radar chart of health score components."""
    categories = list(breakdown.keys())
    max_vals = {"activity": 30, "momentum": 20, "responsiveness": 20,
                "recency": 20, "release_cadence": 10}

    # Normalise to 0-100
    values = [
        round(breakdown.get(c, 0) / max_vals.get(c, 10) * 100)
        for c in categories
    ]
    labels = [c.replace("_", " ").title() for c in categories]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values + [values[0]],
        theta=labels + [labels[0]],
        fill="toself",
        fillcolor="rgba(240,185,11,0.2)",
        line=dict(color="#F0B90B", width=2),
        name="Health",
        hovertemplate="%{theta}: %{r}/100<extra></extra>"
    ))
    fig.update_layout(
        title=f"<b>{repo_name} — Health Breakdown</b>",
        height=380, template="plotly_dark",
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        margin=dict(l=40, r=40, t=50, b=40),
    )
    return fig


def generate_issues_chart(issues: dict, repo_name: str) -> go.Figure:
    """Bar chart comparing open vs closed issues + breakdown."""
    categories = ["Open Issues", "Closed Issues", "Bug Reports", "Feature Requests"]
    values = [
        issues.get("open_count", 0),
        issues.get("closed_count", 0),
        issues.get("bug_count", 0),
        issues.get("feature_count", 0),
    ]
    colors = ["#ef4444", "#22c55e", "#f97316", "#3b82f6"]

    fig = go.Figure(go.Bar(
        x=categories, y=values,
        marker=dict(color=colors),
        hovertemplate="%{x}: %{y}<extra></extra>"
    ))
    fig.update_layout(
        title=f"<b>{repo_name} — Issue Breakdown</b>",
        height=360, template="plotly_dark",
        margin=dict(l=40, r=40, t=50, b=40),
        yaxis_title="Count",
    )
    return fig


def generate_score_gauge(score: int, label: str, repo_name: str) -> go.Figure:
    """Gauge chart for the overall health score."""
    color = (
        "#22c55e" if score >= 75 else
        "#F0B90B" if score >= 50 else
        "#f97316" if score >= 30 else
        "#ef4444"
    )
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=score,
        title={"text": f"{repo_name}<br><span style='font-size:.8em'>{label}</span>"},
        gauge={
            "axis": {"range": [0, 100], "tickwidth": 1},
            "bar":  {"color": color},
            "steps": [
                {"range": [0,  30], "color": "#2d0a0a"},
                {"range": [30, 60], "color": "#1a1500"},
                {"range": [60, 80], "color": "#052e16"},
                {"range": [80,100], "color": "#052e16"},
            ],
            "threshold": {"line": {"color": "white", "width": 3}, "value": score},
        },
        number={"suffix": "/100"},
    ))
    fig.update_layout(
        height=320, template="plotly_dark",
        margin=dict(l=30, r=30, t=60, b=20),
    )
    return fig


def run_chart_generator(repo_data: dict) -> dict:
    """Generate all charts from repo_data."""
    try:
        meta     = repo_data.get("meta", {})
        commits  = repo_data.get("commits", {})
        issues   = repo_data.get("issues", {})
        health   = repo_data.get("health", {})
        name     = meta.get("repo", "repo")
        weekly   = commits.get("weekly", [])

        charts = {}

        if len(weekly) >= 4:
            charts["commits"]  = generate_commit_chart(weekly, name)

        if health.get("breakdown"):
            charts["radar"]    = generate_health_radar(health["breakdown"], name)

        charts["issues"]       = generate_issues_chart(issues, name)
        charts["gauge"]        = generate_score_gauge(
            health.get("score", 0), health.get("label", ""), name
        )

        return {"success": True, "charts": charts}
    except Exception as e:
        print(f"  ⚠️  Chart generation failed: {e}")
        return {"success": False, "charts": {}}
