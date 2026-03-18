# ============================================================
# agents/report_writer.py — Agent 4: Synthesise final report
# ============================================================

from tools.github_tools import get_llm, clean_output, fmt_number


def run_report_writer(repo_data: dict, activity_data: dict, community_data: dict) -> dict:
    """
    Agent 4: Combine all agent outputs into a final actionable report.
    Answers: Is this repo worth depending on? Should I contribute? Is it dying?
    """
    print("  📝 Report Writer: synthesising final verdict...")

    meta    = repo_data.get("meta", {})
    health  = repo_data.get("health", {})
    commits = repo_data.get("commits", {})
    releases = repo_data.get("releases", {})
    contributors = repo_data.get("contributors", {})

    context = f"""
REPOSITORY: {meta.get('full_name')} ({meta.get('url')})
Description: {meta.get('description')}
Language: {meta.get('language')} | License: {meta.get('license')}
Stars: {fmt_number(meta.get('stars',0))} | Forks: {fmt_number(meta.get('forks',0))} | Watchers: {fmt_number(meta.get('watchers',0))}
Topics: {', '.join(meta.get('topics', [])) or 'none'}

HEALTH SCORE: {health.get('score')}/100 ({health.get('label')})

ACTIVITY SIGNAL: {activity_data.get('signal')}
Commit trend: {commits.get('trend_pct', 0):+.1f}% vs prior period
Active weeks: {commits.get('active_weeks', 0)}/12 recent weeks
Last push: {meta.get('days_since_push')} days ago
Latest release: {releases.get('latest_tag', 'none')} ({releases.get('days_since_release', 9999)} days ago)

COMMUNITY SENTIMENT: {community_data.get('sentiment_label')}
Open issues: {repo_data.get('issues', {}).get('open_count', 0)}
Contributors: {contributors.get('contributor_count', 0)}
Bus factor risk: {contributors.get('top_contributor_pct', 0)}% single-person dependency

ACTIVITY ANALYSIS:
{activity_data.get('analysis', '')}

COMMUNITY ANALYSIS:
{community_data.get('sentiment', '')}
"""

    llm = get_llm()
    prompt = f"""You are a senior engineering lead writing a repo health report for your team.

Write a concise, actionable report with these sections:

## Verdict
One sentence: overall assessment (Healthy/At Risk/Dying/Dead)
Health Score: X/100

## Why This Matters
2-3 sentences on what this repo does and why its health matters to developers depending on it.

## Strengths
3 specific bullet points with real numbers.

## Risks
3 specific bullet points with real numbers.

## Recommendation
One clear action: ADOPT / USE WITH CAUTION / MONITOR / REPLACE
Explain the reasoning in 2-3 sentences.

## Next Steps
2-3 concrete actions for a developer depending on this repo.

Keep it under 350 words. Be direct. A developer should finish reading this in 60 seconds.

{context}"""

    try:
        response = llm.invoke(prompt)
        report = clean_output(response)
    except Exception as e:
        report = f"Report generation failed: {e}"

    # Determine overall verdict label
    signal = activity_data.get("signal", "UNKNOWN")
    sentiment = community_data.get("sentiment_label", "UNKNOWN")
    score = health.get("score", 0)

    if score >= 75:
        verdict = "ADOPT"
    elif score >= 50:
        verdict = "USE WITH CAUTION"
    elif score >= 30:
        verdict = "MONITOR"
    else:
        verdict = "REPLACE"

    print(f"     ✅ Verdict: {verdict} (score: {score}/100)")
    return {
        "report":  report,
        "verdict": verdict,
        "score":   score,
    }
