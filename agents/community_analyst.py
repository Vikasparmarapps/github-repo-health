# ============================================================
# agents/community_analyst.py — Agent 3: Community sentiment
# ============================================================
# Analyses issue titles, labels, bug/feature ratio.
# Runs in PARALLEL with activity_analyst.

from tools.github_tools import get_llm, clean_output


def run_community_analyst(repo_data: dict) -> dict:
    """
    Agent 3: Gauge community health from issue patterns and engagement signals.
    """
    print("  💬 Community Analyst: analysing issues and community signals...")

    meta   = repo_data.get("meta", {})
    issues = repo_data.get("issues", {})
    contributors = repo_data.get("contributors", {})

    open_titles   = issues.get("open_titles", [])
    closed_titles = issues.get("closed_titles", [])

    context = f"""
Repository: {meta.get('full_name')}
Open issues: {issues.get('open_count', 0)}
Closed issues (recent sample): {issues.get('closed_count', 0)}
Bug-labelled issues: {issues.get('bug_count', 0)}
Feature requests: {issues.get('feature_count', 0)}
Avg comments per issue: {issues.get('avg_comments', 0)}
Contributors: {contributors.get('contributor_count', 0)}
Top contributors: {', '.join(contributors.get('top_logins', [])[:3])}

Sample of open issue titles (what people are reporting/requesting):
{chr(10).join(f'- {t}' for t in open_titles[:15])}

Sample of recently closed issues (what maintainers are fixing):
{chr(10).join(f'- {t}' for t in closed_titles[:8])}
"""

    llm = get_llm()
    prompt = f"""You are a community health analyst for open source projects.

Analyse the community signals for this repository and provide:
1. SENTIMENT: one of ACTIVE / ENGAGED / QUIET / NEGLECTED
2. Community health summary (2-3 bullet points)
3. What the open issues reveal about user pain points
4. Maintainer responsiveness assessment
5. Overall recommendation: is this community growing, stable, or declining?

Be direct and use the actual issue data. Under 200 words.

{context}"""

    try:
        response = llm.invoke(prompt)
        sentiment_text = clean_output(response)
        sentiment = "QUIET"
        for s in ["ACTIVE", "ENGAGED", "NEGLECTED", "QUIET"]:
            if s in sentiment_text.upper():
                sentiment = s
                break
    except Exception as e:
        sentiment_text = f"Analysis failed: {e}"
        sentiment = "UNKNOWN"

    print(f"     ✅ Community sentiment: {sentiment}")
    return {
        "agent":          "Community Analyst",
        "success":        True,
        "sentiment":      sentiment_text,
        "sentiment_label": sentiment,
        "open_issues":    issues.get("open_count", 0),
        "bug_count":      issues.get("bug_count", 0),
        "feature_count":  issues.get("feature_count", 0),
    }
