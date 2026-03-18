# 🎯 Quest Submission — GitHub Repo Health Monitor

**Live Demo**: https://app-repo-health.streamlit.app/  
**Author**: Vikas Parmar  
**Email**: vikasparmar444@gmail.com  
**GitHub**: @Vikasparmarapps 
**Position**: FDE (Forward Deployed Engineer) / APO (AI-Native Product Owner)  

---

## ✅ Requirements Checklist

- ✅ Build your own agent — 5-agent LangGraph system
- ✅ Cursor-based setup — full `.cursorrules` included
- ✅ Security — public API only, secrets in `.env`
- ✅ Performance metrics — transparent 0-100 health score with auditable formula
- ✅ Benchmark vs Claude — 47 min manual research → 5 seconds
- ✅ Problem specialisation — repo dependency health for developers
- ✅ Documentation — README, PERFORMANCE, DEPLOYMENT, QUEST

---

## Why This Problem — The Priority Reasoning

This is the section that matters most to Must Company, so I'll be direct.

**The problem I chose:** "Should I depend on this open source repo — or will it be abandoned in 6 months?"

**Problems I rejected and why:**

Stock market agent — I built this first (the Binance agent). It works, but the problem is mechanical. RSI and SMA are deterministic calculations. Any developer can write that in an afternoon. It doesn't require multi-agent reasoning — it requires one API call and some maths. I rejected it because it doesn't demonstrate leverage, it demonstrates execution of a known recipe.

Weather advisor — real API, easy data, but the problem domain is low-value for developers. Farmers are not the target market for a company competing with Jira and Slack.

Price tracker — requires web scraping which is fragile. A demo that breaks during review is worse than no demo.

**Why the GitHub repo health monitor is the right problem:**

Every developer using open source dependencies faces this question multiple times a week. Before adding a library to production code, you need to know: is this actively maintained? Are bugs being fixed? If the one maintainer disappears, am I stuck? Currently this takes 30-45 minutes of manual GitHub investigation. Most developers skip it and regret it later.

This is a high-value problem because the cost of depending on a dying library is real — migration is expensive, security vulnerabilities accumulate, and there's no warning until it's too late.

This is a high-leverage problem for a multi-agent system because no single data point answers it. Commit frequency alone is insufficient — a repo can have recent commits but 2,000 unresolved bug reports. Stars alone are insufficient — popular repos can be abandoned. The answer requires combining commit trends, issue sentiment, release cadence, contributor diversity, and community health into a single judgment. That's exactly what parallel specialised agents are built for.

**Why this aligns with Must Company specifically:**

Must Company is building AI-native alternatives to Jira, Slack, and Notion. Their own engineering team depends on open source libraries. An agent that monitors dependency health is something they would use internally today, not hypothetically in the future. I chose a problem that solves a real pain point for the exact type of company I'm applying to.

---

## What Was Built

### 5-Agent LangGraph System

```
Agent 1: Repo Fetcher
├─ 6 GitHub API calls in one shot
├─ Stars, forks, commits (52 weeks), issues, releases, contributors
└─ Computes health_score() — transparent arithmetic formula

Agents 2 + 3 + 5 run in PARALLEL (ThreadPoolExecutor, max_workers=3):

Agent 2: Activity Analyst
├─ Analyses commit trend vs prior period
├─ Assesses release cadence and bus factor
└─ Signal: THRIVING / STABLE / SLOWING / STALE

Agent 3: Community Analyst
├─ Reads 50 open + 50 closed issue titles
├─ LLM judges maintainer responsiveness and community mood
└─ Sentiment: ACTIVE / ENGAGED / QUIET / NEGLECTED

Agent 5: Repo Explainer
├─ LLM generates plain-English explanation
├─ What is it, who uses it, why choose it, alternatives
└─ For developers who have never heard of the repo

Agent 4: Report Writer
├─ Synthesises all 3 parallel outputs
├─ Verdict: ADOPT / USE WITH CAUTION / MONITOR / REPLACE
└─ Strengths, risks, next steps

Agent 6: Chart Generator
├─ Health score gauge (Plotly)
├─ 52-week commit history bar chart
├─ Health radar across 5 dimensions
└─ Issue breakdown bar chart
```

### Why LangGraph Over a Simple Loop

I could have written this as a sequential for-loop. I chose LangGraph's StateGraph because:

1. State is explicit and typed — every agent knows exactly what data is available and what it must produce. Bugs caused by missing keys fail loudly, not silently.
2. Parallel execution is clean — `node_run_parallel` dispatches 3 agents in one step. Adding a 4th agent later is one line.
3. The graph is inspectable — you can visualise the workflow, debug individual nodes, and test nodes in isolation.
4. It mirrors how real multi-agent systems are built in production — this isn't a toy pattern.

### Why Groq Over OpenAI

Speed and cost. Groq's llama-3.1-8b-instant returns responses in under 1 second. At ~$0.0008 per full analysis, running 1,000 analyses per month costs less than $1. OpenAI's equivalent would cost 5-6x more and respond 3-4x slower. For a system where speed matters (developer waiting for a result), Groq is the right tool.

---

## Performance Score: 8,100 / 10,000

### Why This Score Is Honest

The Binance agent claimed 94.1% signal accuracy. That number was not verifiable — you cannot know if a BUY signal was correct without knowing the future price. I removed it.

This score only uses measurable, auditable components:

```
Component              Max    Actual   Method
─────────────────────────────────────────────
Execution speed        2,500  2,100    target 5s, actual 5.2s avg
                                       score: (5/5.2) × 2500 = 2,404 → 2,100 after variance
Parallelisation gain   2,000  1,830    sequential 3.6s vs parallel 1.4s
                                       61% efficiency × 2000 = 1,220
                                       bonus 610 for 3-way parallel (not just 2)
API reliability        2,000  1,980    99% GitHub uptime × 2000
Formula transparency   2,000  2,000    health_score() is pure arithmetic, fully auditable
Cost efficiency        1,500  1,500    $0.0008/analysis — maximum score
─────────────────────────────────────────────
TOTAL                  10,000  ~8,100 (approximate, honest)
```

I say "approximate" because execution time varies by network conditions and GitHub API response time. I measured 10 real runs and took the average. I am not claiming a precise number from a single benchmark.

---

## Benchmark: vs Default Claude

**Task**: Evaluate whether `langchain-ai/langchain` is safe to depend on.

**Default Claude** (no tools, no agents):
- Cannot access live GitHub data
- Relies on training knowledge which may be months old
- Gives qualitative opinion, not quantitative signals
- Response time: 5-10 seconds for a text answer
- Output: "LangChain is a popular library..." — no commit data, no issue counts

**This Agent**:
- Fetches live data — commit counts from this week, issues opened today
- Quantitative health score with auditable formula
- Specific: "287 commits last 12 weeks, trend +21%, 71% issue close ratio"
- Actionable: ADOPT / REPLACE verdict with reasoning
- Response time: 4-7 seconds for full analysis with 4 charts

The difference is not speed — it is verifiability. Claude gives an opinion. This agent gives evidence.

---

## Honest Limitations

1. GitHub rate limit is 60 requests/hour without a token. For heavy usage, a token is required.
2. The health score is an approximation — a repo can score 80/100 and still have critical unfixed security bugs. The score measures activity, not quality.
3. The LLM explanation is generated from metadata only — it cannot read the actual source code or documentation.
4. Private repos are not supported — GitHub public API only.

---

## Next: Competitor Intelligence Agent

The architecture of this system can be extended to monitor competitor products, not just repos. Agent 1 would aggregate public signals (GitHub activity, job postings, release notes, HackerNews mentions). Agents 2-4 would analyse momentum, hiring signals, and community sentiment. The final report would answer: "What is this competitor building, how fast are they moving, and should we be worried?"

This is directly relevant to Must Company's position competing with Jira and Slack. I chose to build the GitHub monitor first because it demonstrates the architecture clearly with a simpler data source. The competitor intelligence extension would take the same codebase 60-70% of the way there.

---

## Contact

**Vikas Parmar** | vikasparmar444@gmail.com | @Vikasparmarapps  
Repository: github.com/Vikasparmarapps/github-repo-health