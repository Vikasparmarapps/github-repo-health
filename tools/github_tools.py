# ============================================================
# tools/github_tools.py — GitHub API + shared utilities
# ============================================================
# All GitHub API calls live here. One job: fetch repo data.
#
# GitHub public endpoints used (no auth needed for public repos):
#   /repos/{owner}/{repo}              → repo metadata
#   /repos/{owner}/{repo}/commits      → commit history
#   /repos/{owner}/{repo}/issues       → open/closed issues
#   /repos/{owner}/{repo}/releases     → release history
#   /repos/{owner}/{repo}/contributors → top contributors
#   /repos/{owner}/{repo}/stats/commit_activity → weekly commit stats

import re
import requests
from datetime import datetime, timezone
from config import (
    GITHUB_BASE_URL, GITHUB_TOKEN,
    GROQ_API_KEY, GROQ_MODEL, TEMPERATURE, MAX_TOKENS,
    COMMIT_LOOKBACK_DAYS, ISSUES_LIMIT, RELEASES_LIMIT,
)


# ── LLM Factory ──────────────────────────────────────────────

def get_llm(temperature: float = TEMPERATURE):
    from langchain_groq import ChatGroq
    return ChatGroq(
        model=GROQ_MODEL,
        groq_api_key=GROQ_API_KEY,
        temperature=temperature,
        max_tokens=MAX_TOKENS,
    )


def clean_output(text) -> str:
    if hasattr(text, "content"):
        text = text.content
    return re.sub(r"```(?:\w+)?|```", "", str(text)).strip()


# ── Repo Detection ────────────────────────────────────────────

def parse_repo(query: str) -> tuple[str, str]:
    """
    Extract owner/repo from various input formats.
    'langchain-ai/langchain'  → ('langchain-ai', 'langchain')
    'github.com/user/repo'   → ('user', 'repo')
    'analyze streamlit repo' → ('streamlit', 'streamlit')  [best guess]
    """
    # Full URL
    url_match = re.search(r'github\.com/([^/\s]+)/([^/\s]+)', query)
    if url_match:
        return url_match.group(1), url_match.group(2).rstrip('/')

    # owner/repo format
    slash_match = re.search(r'\b([a-zA-Z0-9_.-]+)/([a-zA-Z0-9_.-]+)\b', query)
    if slash_match:
        return slash_match.group(1), slash_match.group(2)

    # Single word — try as repo name with same owner
    words = re.findall(r'\b[a-zA-Z0-9_.-]{3,}\b', query.lower())
    stop = {'analyze','analyse','repo','repository','check','show','health',
            'monitor','tell','about','the','me','please','github'}
    candidates = [w for w in words if w not in stop]
    if candidates:
        name = candidates[0]
        return name, name

    return "streamlit", "streamlit"


# ── GitHub API Helpers ────────────────────────────────────────

def _headers() -> dict:
    h = {"Accept": "application/vnd.github+json",
         "X-GitHub-Api-Version": "2022-11-28"}
    if GITHUB_TOKEN:
        h["Authorization"] = f"Bearer {GITHUB_TOKEN}"
    return h


def _get(path: str, params: dict = None) -> dict | list | None:
    url = f"{GITHUB_BASE_URL}{path}"
    try:
        r = requests.get(url, headers=_headers(), params=params, timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"  GitHub API error {path}: {e}")
        return None


# ── Core Fetchers ─────────────────────────────────────────────

def get_repo_meta(owner: str, repo: str) -> dict:
    """Fetch core repo metadata."""
    data = _get(f"/repos/{owner}/{repo}")
    if not data or "id" not in data:
        return {"success": False, "error": f"Repo {owner}/{repo} not found"}

    pushed = data.get("pushed_at", "")
    days_since_push = 9999
    if pushed:
        dt = datetime.fromisoformat(pushed.replace("Z", "+00:00"))
        days_since_push = (datetime.now(timezone.utc) - dt).days

    return {
        "success":          True,
        "owner":            owner,
        "repo":             repo,
        "full_name":        data.get("full_name", f"{owner}/{repo}"),
        "description":      data.get("description", "No description"),
        "stars":            data.get("stargazers_count", 0),
        "forks":            data.get("forks_count", 0),
        "watchers":         data.get("watchers_count", 0),
        "open_issues":      data.get("open_issues_count", 0),
        "language":         data.get("language", "Unknown"),
        "license":          (data.get("license") or {}).get("spdx_id", "None"),
        "created_at":       data.get("created_at", ""),
        "pushed_at":        pushed,
        "days_since_push":  days_since_push,
        "default_branch":   data.get("default_branch", "main"),
        "topics":           data.get("topics", []),
        "has_wiki":         data.get("has_wiki", False),
        "archived":         data.get("archived", False),
        "disabled":         data.get("disabled", False),
        "url":              data.get("html_url", ""),
    }


def get_commit_activity(owner: str, repo: str) -> dict:
    """
    Fetch weekly commit stats for the last 52 weeks.
    Returns list of weekly totals + derived trend metrics.
    """
    data = _get(f"/repos/{owner}/{repo}/stats/commit_activity")
    if not data or not isinstance(data, list):
        return {"success": False, "weekly": [], "total_year": 0}

    weekly = [w.get("total", 0) for w in data]   # 52 values, oldest first
    recent_4  = sum(weekly[-4:])
    recent_12 = sum(weekly[-12:])
    prev_12   = sum(weekly[-24:-12])
    total_year = sum(weekly)

    # Trend: compare last 12 weeks vs prior 12 weeks
    if prev_12 > 0:
        trend_pct = ((recent_12 - prev_12) / prev_12) * 100
    else:
        trend_pct = 100.0 if recent_12 > 0 else 0.0

    # Active weeks in last 12
    active_weeks = sum(1 for w in weekly[-12:] if w > 0)

    return {
        "success":       True,
        "weekly":        weekly,          # list of 52 ints for charting
        "recent_4w":     recent_4,
        "recent_12w":    recent_12,
        "prev_12w":      prev_12,
        "total_year":    total_year,
        "trend_pct":     round(trend_pct, 1),
        "active_weeks":  active_weeks,    # out of last 12
        "avg_per_week":  round(total_year / 52, 1),
    }


def get_issues_data(owner: str, repo: str) -> dict:
    """Fetch recent issues — both open and closed — for sentiment analysis."""
    open_data   = _get(f"/repos/{owner}/{repo}/issues",
                       {"state": "open",   "per_page": ISSUES_LIMIT, "sort": "updated"})
    closed_data = _get(f"/repos/{owner}/{repo}/issues",
                       {"state": "closed", "per_page": ISSUES_LIMIT, "sort": "updated"})

    def parse(items):
        if not items or not isinstance(items, list):
            return []
        return [
            {
                "title":    i.get("title", ""),
                "state":    i.get("state", ""),
                "comments": i.get("comments", 0),
                "labels":   [l["name"] for l in i.get("labels", [])],
                "created":  i.get("created_at", ""),
            }
            for i in items
            if "pull_request" not in i   # exclude PRs
        ]

    open_issues   = parse(open_data)
    closed_issues = parse(closed_data)

    # Bug/feature ratio
    bug_labels = {"bug", "defect", "error", "crash", "fix"}
    feat_labels = {"enhancement", "feature", "improvement", "request"}

    bugs     = sum(1 for i in open_issues
                   if any(l.lower() in bug_labels for l in i["labels"]))
    features = sum(1 for i in open_issues
                   if any(l.lower() in feat_labels for l in i["labels"]))

    return {
        "success":        True,
        "open_count":     len(open_issues),
        "closed_count":   len(closed_issues),
        "open_titles":    [i["title"] for i in open_issues[:20]],
        "closed_titles":  [i["title"] for i in closed_issues[:10]],
        "bug_count":      bugs,
        "feature_count":  features,
        "avg_comments":   round(
            sum(i["comments"] for i in open_issues) / max(len(open_issues), 1), 1
        ),
    }


def get_releases(owner: str, repo: str) -> dict:
    """Fetch recent releases to gauge release velocity."""
    data = _get(f"/repos/{owner}/{repo}/releases",
                {"per_page": RELEASES_LIMIT})
    if not data or not isinstance(data, list):
        return {"success": False, "count": 0, "latest": None, "days_since": 9999}

    releases = data
    latest = releases[0] if releases else None

    days_since_release = 9999
    if latest and latest.get("published_at"):
        dt = datetime.fromisoformat(latest["published_at"].replace("Z", "+00:00"))
        days_since_release = (datetime.now(timezone.utc) - dt).days

    return {
        "success":            True,
        "count":              len(releases),
        "latest_tag":         (latest or {}).get("tag_name", "none"),
        "latest_name":        (latest or {}).get("name", ""),
        "days_since_release": days_since_release,
        "is_prerelease":      (latest or {}).get("prerelease", False),
        "release_names":      [r.get("tag_name", "") for r in releases[:5]],
    }


def get_contributors(owner: str, repo: str) -> dict:
    """Fetch top contributors count and activity."""
    data = _get(f"/repos/{owner}/{repo}/contributors", {"per_page": 30})
    if not data or not isinstance(data, list):
        return {"success": False, "total": 0, "top_contributor_pct": 0}

    total_contributions = sum(c.get("contributions", 0) for c in data)
    top = data[0].get("contributions", 0) if data else 0
    top_pct = round((top / total_contributions * 100) if total_contributions else 0, 1)

    return {
        "success":             True,
        "contributor_count":   len(data),
        "total_contributions": total_contributions,
        "top_contributor_pct": top_pct,   # % of commits from single person (bus factor)
        "top_logins":          [c.get("login", "") for c in data[:5]],
    }


# ── Formatting Helpers ────────────────────────────────────────

def fmt_number(n: int) -> str:
    if n >= 1_000_000:
        return f"{n/1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n/1_000:.1f}k"
    return str(n)


def health_score(meta: dict, commits: dict, issues: dict, releases: dict) -> dict:
    """
    Compute a 0–100 health score from measurable signals.
    Transparent formula — no fake accuracy claims.
    """
    score = 0
    breakdown = {}

    # Activity (30 pts) — are people committing?
    active_wks = commits.get("active_weeks", 0)
    activity_pts = min(30, int(active_wks / 12 * 30))
    score += activity_pts
    breakdown["activity"] = activity_pts

    # Momentum (20 pts) — is it growing or dying?
    trend = commits.get("trend_pct", 0)
    if trend >= 20:
        momentum_pts = 20
    elif trend >= 0:
        momentum_pts = 10
    elif trend >= -30:
        momentum_pts = 5
    else:
        momentum_pts = 0
    score += momentum_pts
    breakdown["momentum"] = momentum_pts

    # Responsiveness (20 pts) — how fast do issues get closed?
    open_c  = issues.get("open_count", 0)
    close_c = issues.get("closed_count", 1)
    ratio   = close_c / max(open_c + close_c, 1)
    resp_pts = min(20, int(ratio * 20))
    score += resp_pts
    breakdown["responsiveness"] = resp_pts

    # Recency (20 pts) — when was last push?
    days = meta.get("days_since_push", 9999)
    if days <= 7:
        recency_pts = 20
    elif days <= 30:
        recency_pts = 15
    elif days <= 90:
        recency_pts = 8
    else:
        recency_pts = 0
    score += recency_pts
    breakdown["recency"] = recency_pts

    # Release cadence (10 pts)
    days_rel = releases.get("days_since_release", 9999)
    if days_rel <= 30:
        release_pts = 10
    elif days_rel <= 90:
        release_pts = 6
    elif days_rel <= 180:
        release_pts = 3
    else:
        release_pts = 0
    score += release_pts
    breakdown["release_cadence"] = release_pts

    # Penalty: archived repo
    if meta.get("archived"):
        score = max(0, score - 30)

    label = (
        "Excellent" if score >= 80 else
        "Healthy"   if score >= 60 else
        "Moderate"  if score >= 40 else
        "At Risk"   if score >= 20 else
        "Inactive"
    )

    return {"score": score, "label": label, "breakdown": breakdown}
