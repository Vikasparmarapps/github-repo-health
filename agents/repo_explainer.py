# ============================================================
# agents/repo_explainer.py — Agent 5: Explain the repo
# ============================================================
# Answers: What is this? What is it used for? Who uses it?
# Why would I choose this over alternatives?
# Runs in PARALLEL with activity + community analysts.

from tools.github_tools import get_llm, clean_output


def run_repo_explainer(repo_data: dict) -> dict:
    """
    Agent 5: Plain-English explanation of what this repo is,
    what problem it solves, who uses it, and when to use it.
    """
    print("  🧠 Repo Explainer: generating plain-English explanation...")

    meta         = repo_data.get("meta", {})
    releases     = repo_data.get("releases", {})
    contributors = repo_data.get("contributors", {})

    context = f"""
Repository: {meta.get('full_name')}
Description: {meta.get('description', 'No description')}
Primary language: {meta.get('language', 'Unknown')}
Topics/tags: {', '.join(meta.get('topics', [])) or 'none'}
Stars: {meta.get('stars', 0):,}
Forks: {meta.get('forks', 0):,}
License: {meta.get('license', 'Unknown')}
Latest release: {releases.get('latest_tag', 'none')}
Top contributors: {', '.join(contributors.get('top_logins', [])[:5])}
Created: {meta.get('created_at', '')[:10]}
URL: {meta.get('url', '')}
"""

    llm = get_llm(temperature=0.3)
    prompt = f"""You are explaining a GitHub repository to a developer who has never heard of it.

Based on the repository information below, write a clear explanation with exactly these sections:

## What is it?
One paragraph (3-4 sentences). What does this repo do? What problem does it solve?
Explain it simply — as if talking to a smart developer who doesn't know this specific tool.

## What is it used for?
3-5 concrete real-world use cases. Each one should be a specific example, not vague.
Format: bullet points starting with a use case name in bold, then one sentence explanation.

## Who uses it?
2-3 sentences. What type of developers or companies use this?
Is it for beginners, experts, startups, enterprises? Give real examples if you know them.

## Why choose this?
2-3 bullet points. What makes this repo stand out?
What problem does it solve better than alternatives? Be specific.

## Main alternatives
List 2-3 alternative tools/libraries for the same problem.
One line each: "**AlternativeName** — how it differs"

Keep the entire response under 400 words. Be specific and practical, not marketing-speak.

{context}"""

    try:
        response = llm.invoke(prompt)
        explanation = clean_output(response)
    except Exception as e:
        explanation = f"Explanation failed: {e}"

    print(f"     ✅ Explanation generated for {meta.get('full_name', 'repo')}")
    return {
        "agent":       "Repo Explainer",
        "success":     True,
        "explanation": explanation,
        "repo_name":   meta.get("full_name", ""),
        "language":    meta.get("language", ""),
        "topics":      meta.get("topics", []),
    }
