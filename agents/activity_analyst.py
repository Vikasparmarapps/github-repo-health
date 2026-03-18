# ============================================================
# agents/activity_analyst.py — Agent 2: Technical analysis
# ============================================================
# Analyses commit patterns, release velocity, bus factor.
# Runs in PARALLEL with sentiment_analyst.

from tools.github_tools import get_llm, clean_output


def run_activity_analyst(repo_data: dict) -> dict:
    """
    Agent 2: Deep-dive into commit trends, release cadence, contributor risk.
    Returns structured technical analysis with a BUY/HOLD/SELL-equivalent signal.
    """
    print("  📊 Activity Analyst: analysing commit patterns...")

    meta        = repo_data.get("meta", {})
    commits     = repo_data.get("commits", {})
    releases    = repo_data.get("releases", {})
    contributors = repo_data.get("contributors", {})
    health      = repo_data.get("health", {})

    # Build context for LLM
    context = f"""
Repository: {meta.get('full_name')}
Stars: {meta.get('stars', 0):,} | Forks: {meta.get('forks', 0):,}
Language: {meta.get('language')} | License: {meta.get('license')}
Last push: {meta.get('days_since_push')} days ago
Archived: {meta.get('archived')}

Commit Activity (last 52 weeks):
- Total commits this year: {commits.get('total_year', 0)}
- Last 4 weeks: {commits.get('recent_4w', 0)} commits
- Last 12 weeks: {commits.get('recent_12w', 0)} commits
- Prior 12 weeks: {commits.get('prev_12w', 0)} commits
- Trend: {commits.get('trend_pct', 0):+.1f}% vs prior period
- Active weeks (of last 12): {commits.get('active_weeks', 0)}/12
- Average per week: {commits.get('avg_per_week', 0)}

Release Cadence:
- Recent releases: {releases.get('count', 0)}
- Latest: {releases.get('latest_tag', 'none')} ({releases.get('days_since_release', 9999)} days ago)
- Is prerelease: {releases.get('is_prerelease', False)}

Contributor Health:
- Unique contributors (top 30): {contributors.get('contributor_count', 0)}
- Top contributor share: {contributors.get('top_contributor_pct', 0)}% of all commits
  (high % = bus factor risk — project depends on one person)

Health Score: {health.get('score', 0)}/100 ({health.get('label', '')})
Score breakdown: {health.get('breakdown', {})}
"""

    llm = get_llm()
    prompt = f"""You are a senior developer evaluating open source repository health.

Analyse this repository's technical activity and provide:
1. SIGNAL: one of THRIVING / STABLE / SLOWING / STALE (based on commit trends)
2. Key strengths (2-3 bullet points, specific numbers)
3. Key risks (2-3 bullet points, specific numbers)
4. Bus factor assessment (is the project too dependent on one person?)
5. Release cadence verdict (frequent/normal/slow/absent)

Be specific and direct. Use the actual numbers. No vague language.
Keep total response under 250 words.

{context}"""

    try:
        response = llm.invoke(prompt)
        analysis = clean_output(response)
        signal = "STABLE"
        for s in ["THRIVING", "SLOWING", "STALE", "STABLE"]:
            if s in analysis.upper():
                signal = s
                break
    except Exception as e:
        analysis = f"Analysis failed: {e}"
        signal = "UNKNOWN"

    print(f"     ✅ Activity signal: {signal}")
    return {
        "agent":    "Activity Analyst",
        "success":  True,
        "analysis": analysis,
        "signal":   signal,
        "trend_pct": commits.get("trend_pct", 0),
        "active_weeks": commits.get("active_weeks", 0),
    }
