# ============================================================
# config.py — All settings. Change only this file.
# ============================================================

import os
from dotenv import load_dotenv

load_dotenv()

# ── Groq LLM
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
GROQ_MODEL   = "llama-3.1-8b-instant"
TEMPERATURE  = 0.2
MAX_TOKENS   = 1024

# ── GitHub API (public repos need no auth, optional token raises rate limit)
GITHUB_BASE_URL = "https://api.github.com"
GITHUB_TOKEN    = os.environ.get("GITHUB_TOKEN", "")   # optional but recommended

# ── Analysis settings
COMMIT_LOOKBACK_DAYS = 90     # how many days back to analyse commits
ISSUES_LIMIT         = 50     # max issues to fetch for sentiment
RELEASES_LIMIT       = 10     # recent releases to check

# ── UI settings
APP_TITLE    = "🔍 GitHub Repo Health Monitor"
APP_SUBTITLE = "AI-powered repo analysis · Powered by LangGraph · Groq · GitHub API"

# ── Popular repo suggestions shown in UI
SUGGESTED_REPOS = [
    "langchain-ai/langchain",
    "streamlit/streamlit",
    "tiangolo/fastapi",
    "microsoft/autogen",
    "openai/openai-python",
    "facebookresearch/llama",
]

if GROQ_API_KEY:
    print(f"✅ Groq API key loaded — model: {GROQ_MODEL}")
else:
    print("❌ GROQ_API_KEY not set — add it to .env file")