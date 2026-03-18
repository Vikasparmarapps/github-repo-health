# ============================================================
# agents/repo_fetcher.py — Agent 1: Fetch all repo data
# ============================================================

from tools.github_tools import (
    parse_repo, get_repo_meta, get_commit_activity,
    get_issues_data, get_releases, get_contributors,
    health_score, fmt_number,
)


def run_repo_fetcher(query: str) -> dict:
    """
    Agent 1: Parse the user query, fetch all GitHub data.
    Returns a unified repo_data dict used by all other agents.
    """
    owner, repo = parse_repo(query)
    print(f"  🔍 Repo Fetcher: fetching {owner}/{repo} from GitHub...")

    meta        = get_repo_meta(owner, repo)
    if not meta.get("success"):
        return {"success": False, "error": meta.get("error", "Repo not found"),
                "owner": owner, "repo": repo}

    commits     = get_commit_activity(owner, repo)
    issues      = get_issues_data(owner, repo)
    releases    = get_releases(owner, repo)
    contributors = get_contributors(owner, repo)
    score       = health_score(meta, commits, issues, releases)

    print(f"     ✅ {owner}/{repo} — ⭐ {fmt_number(meta['stars'])} stars | "
          f"Health: {score['score']}/100 ({score['label']})")

    return {
        "success":       True,
        "owner":         owner,
        "repo":          repo,
        "meta":          meta,
        "commits":       commits,
        "issues":        issues,
        "releases":      releases,
        "contributors":  contributors,
        "health":        score,

        # Formatted display values
        "stars_fmt":     fmt_number(meta["stars"]),
        "forks_fmt":     fmt_number(meta["forks"]),
        "issues_fmt":    fmt_number(meta["open_issues"]),
    }
