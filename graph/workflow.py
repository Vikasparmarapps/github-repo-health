# ============================================================
# graph/workflow.py — LangGraph orchestrator
# ============================================================
#
#   START
#     │
#     ▼
#   fetch_repo          ← GitHub API (all data in one shot)
#     │
#     ▼
#   run_agents_parallel ← Activity Analyst + Community Analyst (parallel)
#     │
#     ▼
#   write_report        ← Report Writer synthesises everything
#     │
#     ▼
#   generate_charts     ← Chart Generator
#     │
#     ▼
#   END

from typing import TypedDict
from concurrent.futures import ThreadPoolExecutor, as_completed
from langgraph.graph import StateGraph, END

from agents.repo_fetcher      import run_repo_fetcher
from agents.activity_analyst  import run_activity_analyst
from agents.community_analyst import run_community_analyst
from agents.repo_explainer    import run_repo_explainer
from agents.report_writer     import run_report_writer
from agents.chart_generator   import run_chart_generator


# ── State ─────────────────────────────────────────────────────

class RepoState(TypedDict):
    query:          str
    repo_data:      dict
    activity_data:  dict
    community_data: dict
    explainer_data: dict
    report:         str
    verdict:        str
    charts:         dict
    status:         str
    error:          str


# ── Nodes ─────────────────────────────────────────────────────

def node_fetch_repo(state: RepoState) -> dict:
    repo_data = run_repo_fetcher(state["query"])
    if not repo_data.get("success"):
        return {"repo_data": repo_data, "status": "error",
                "error": repo_data.get("error", "Fetch failed")}
    return {"repo_data": repo_data, "status": "analysing"}


def node_run_parallel(state: RepoState) -> dict:
    repo_data = state["repo_data"]
    activity_data = community_data = explainer_data = {}

    print("🚀 Running Activity + Community + Explainer in parallel...")
    with ThreadPoolExecutor(max_workers=3) as ex:
        futures = {
            ex.submit(run_activity_analyst,  repo_data): "activity",
            ex.submit(run_community_analyst, repo_data): "community",
            ex.submit(run_repo_explainer,    repo_data): "explainer",
        }
        for future in as_completed(futures):
            name = futures[future]
            try:
                result = future.result()
                if name == "activity":
                    activity_data = result
                elif name == "community":
                    community_data = result
                else:
                    explainer_data = result
            except Exception as e:
                print(f"  ⚠️  Agent '{name}' failed: {e}")

    return {"activity_data": activity_data, "community_data": community_data,
            "explainer_data": explainer_data, "status": "writing_report"}


def node_write_report(state: RepoState) -> dict:
    result = run_report_writer(
        repo_data      = state["repo_data"],
        activity_data  = state["activity_data"],
        community_data = state["community_data"],
    )
    return {"report": result["report"], "verdict": result["verdict"],
            "status": "generating_charts"}


def node_generate_charts(state: RepoState) -> dict:
    try:
        result = run_chart_generator(state["repo_data"])
        return {"charts": result.get("charts", {}), "status": "complete"}
    except Exception as e:
        print(f"  ⚠️  Charts failed: {e}")
        return {"charts": {}, "status": "complete"}


# ── Build Graph ───────────────────────────────────────────────

def build_graph():
    g = StateGraph(RepoState)
    g.add_node("fetch_repo",   node_fetch_repo)
    g.add_node("run_parallel", node_run_parallel)
    g.add_node("write_report", node_write_report)
    g.add_node("gen_charts",   node_generate_charts)

    g.set_entry_point("fetch_repo")
    g.add_edge("fetch_repo",   "run_parallel")
    g.add_edge("run_parallel", "write_report")
    g.add_edge("write_report", "gen_charts")
    g.add_edge("gen_charts",   END)

    return g.compile()


# ── Entry Point ───────────────────────────────────────────────

def analyse_repo(query: str) -> dict:
    if not query or not query.strip():
        return {"report": "Please enter a repo name or URL.", "status": "error"}

    graph = build_graph()
    initial: RepoState = {
        "query":          query,
        "repo_data":      {},
        "activity_data":  {},
        "community_data": {},
        "explainer_data": {},
        "report":         "",
        "verdict":        "",
        "charts":         {},
        "status":         "starting",
        "error":          "",
    }
    try:
        return graph.invoke(initial)
    except Exception as e:
        return {"report": f"❌ Analysis failed: {e}", "status": "error", "error": str(e)}