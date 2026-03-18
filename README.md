# 🔍 GitHub Repo Health Monitor

An intelligent multi-agent system that analyses any public GitHub repository and answers the question every developer needs answered: **"Is this repo safe to depend on — or is it dying?"**

**Live Demo**: https://app-repo-health.streamlit.app/  
**Author**: Vikas Parmar (@vikasparmarapps) | **Email**: vikasparmar444@gmail.com  
**GitHub**: github.com/Vikasparmarapps  

---

## 🎯 What It Does

You type any GitHub repo name. In 3-5 seconds you get:

- **Health Score** — 0 to 100, calculated from real measurable signals
- **Verdict** — ADOPT / USE WITH CAUTION / MONITOR / REPLACE
- **Activity Analysis** — commit trends, release cadence, bus factor risk
- **Community Analysis** — issue sentiment, maintainer responsiveness
- **Plain-English Explanation** — what the repo does, who uses it, why choose it
- **4 Interactive Charts** — health gauge, 52-week commits, radar, issue breakdown

---

## 🏗️ Architecture

```
Streamlit UI (repo input)
         ↓
    config.py (ALL settings)
         ↓
╔══════════════════════════════════════════════════════════════╗
║              LangGraph StateGraph Workflow                   ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  Agent 1: Repo Fetcher                                       ║
║  ├─ GitHub /repos/{owner}/{repo}     → metadata             ║
║  ├─ GitHub /stats/commit_activity    → 52-week commits      ║
║  ├─ GitHub /issues                   → open + closed        ║
║  ├─ GitHub /releases                 → release history      ║
║  ├─ GitHub /contributors             → bus factor           ║
║  └─ health_score()                   → 0-100 score         ║
║                 ↓                                            ║
║  ┌────────────────────────────────────────────────────────┐ ║
║  │  Agent 2          Agent 3            Agent 5           │ ║
║  │  Activity         Community          Repo              │ ║
║  │  Analyst          Analyst            Explainer         │ ║
║  │                                                        │ ║
║  │  Commit trends    Issue sentiment    What is it?       │ ║
║  │  Release cadence  Bug/feature ratio  Use cases         │ ║
║  │  Bus factor       Maintainer resp.   Who uses it?      │ ║
║  │  Signal:          Sentiment:         Alternatives      │ ║
║  │  THRIVING/STABLE  ACTIVE/QUIET       Plain English     │ ║
║  │  /SLOWING/STALE   /NEGLECTED                           │ ║
║  │                                                        │ ║
║  │         (all 3 run in PARALLEL)                        │ ║
║  └────────────────────────────────────────────────────────┘ ║
║                 ↓                                            ║
║  Agent 4: Report Writer                                      ║
║  ├─ Synthesises all 3 agent outputs                         ║
║  ├─ Generates verdict: ADOPT/USE WITH CAUTION/MONITOR/      ║
║  │  REPLACE                                                  ║
║  ├─ Lists strengths, risks, next steps                      ║
║  └─ Output: final_report (Markdown)                         ║
║                 ↓                                            ║
║  Agent 5: Chart Generator                                    ║
║  ├─ Health score gauge                                      ║
║  ├─ 52-week commit history bar chart                        ║
║  ├─ Health radar (5 dimensions)                             ║
║  └─ Issue breakdown bar chart                               ║
╚══════════════════════════════════════════════════════════════╝
```

### Tech Stack

| Component | Technology | Purpose |
|---|---|---|
| Orchestration | LangGraph StateGraph | Agent coordination |
| LLM | Groq llama-3.1-8b-instant | Fast inference |
| Data | GitHub Public API | Repo metrics |
| Frontend | Streamlit | Interactive UI |
| Charts | Plotly | Interactive visualisations |
| Concurrency | ThreadPoolExecutor | 3 agents in parallel |

---

## 📁 Project Structure

```
github-repo-health/
├── app.py                      # Streamlit UI — zero business logic
├── config.py                   # ALL settings live here
├── style.css                   # All CSS
├── requirements.txt
├── .env.example
├── .cursorrules                # Cursor AI configuration
│
├── graph/
│   └── workflow.py             # LangGraph StateGraph
│
├── agents/
│   ├── repo_fetcher.py         # Agent 1: fetch all GitHub data
│   ├── activity_analyst.py     # Agent 2: commit + release analysis
│   ├── community_analyst.py    # Agent 3: issue + community sentiment
│   ├── repo_explainer.py       # Agent 5: plain-English explanation
│   ├── report_writer.py        # Agent 4: synthesise final report
│   └── chart_generator.py      # Agent 5: Plotly charts
│
├── tools/
│   └── github_tools.py         # GitHub API + LLM factory + health_score()
│
└── ui/
    ├── styles.py               # CSS via st.html()
    └── components.py           # Reusable UI components
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Groq API key — free at https://console.groq.com
- Internet connection

### Installation

```bash
# 1. Clone
git clone https://github.com/Vikasparmarapps/github-repo-health.git
cd github-repo-health

# 2. Virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure
cp .env.example .env
# Add your GROQ_API_KEY to .env

# 5. Run
streamlit run app.py
```

Open `http://localhost:8501`

---

## 💻 Usage

**Input** — any of these formats work:
```
langchain-ai/langchain
https://github.com/streamlit/streamlit
microsoft/autogen
fastapi
```

**Output example** — `streamlit/streamlit`:
```
Health Score: 82/100 (Excellent)
Verdict: ADOPT

Strengths:
- 287 commits in last 12 weeks — highly active
- Issues close ratio 71% — responsive maintainers  
- 340 unique contributors — low bus factor risk

Risks:
- 847 open issues — large backlog
- Commit trend -8% vs prior period — slight slowdown

Recommendation: ADOPT. Core team is active, releases frequent.
Safe to build production apps on top of Streamlit.
```

---

## ⚙️ Configuration

All settings in `config.py`:

```python
GROQ_MODEL           = "llama-3.1-8b-instant"
COMMIT_LOOKBACK_DAYS = 90
ISSUES_LIMIT         = 50
RELEASES_LIMIT       = 10

SUGGESTED_REPOS = [
    "langchain-ai/langchain",
    "streamlit/streamlit",
    ...
]
```

---

## 🔐 Security

- Public GitHub API only — no auth needed for public repos
- Groq API key stored in `.env` — never committed
- Optional `GITHUB_TOKEN` raises rate limit from 60 to 5,000 req/hr
- No user data stored — stateless analysis

---

## 📊 Health Score Formula

Transparent calculation — no fake accuracy claims:

```
Score (0-100) = Activity(30) + Momentum(20) + Responsiveness(20) 
              + Recency(20) + Release Cadence(10)

Activity:       active weeks in last 12 / 12 × 30
Momentum:       commit trend vs prior 12 weeks
Responsiveness: closed issues / (open + closed) × 20
Recency:        days since last push → 20/15/8/0 pts
Release cadence: days since last release → 10/6/3/0 pts
Penalty:        -30 if repo is archived
```

---

## 📧 Contact

**Vikas Parmar** | vikasparmar444@gmail.com | @Vikasparmarapps

Built with LangGraph + Groq + GitHub API
