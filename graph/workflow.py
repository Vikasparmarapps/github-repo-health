# ============================================================
# graph/workflow.py — LangGraph orchestrator
# ============================================================
# Controls the flow:
#
#   START
#     │
#     ▼
#   fetch_price          ← Binance API (live data)
#     │
#     ▼
#   run_agents_parallel  ← Market Analyst + News Sentiment (parallel)
#     │
#     ▼
#   write_report         ← Report Writer synthesizes everything
#     │
#     ▼
#   END

from typing import TypedDict
from concurrent.futures import ThreadPoolExecutor, as_completed
from langgraph.graph import StateGraph, END

from tools.binance_tools import detect_coin
from agents.price_fetcher  import run_price_fetcher
from agents.market_analyst import run_market_analyst
from agents.news_sentiment import run_news_sentiment
from agents.report_writer  import run_report_writer
from agents.chart_generator import run_chart_generator


# ── State Definition ─────────────────────────────────────────

class CryptoState(TypedDict):
    # Input
    query:          str     # user's original question

    # Detected
    symbol:         str     # e.g. "BTC"

    # Agent outputs
    price_data:     dict    # from price_fetcher
    market_data:    dict    # from market_analyst
    sentiment_data: dict    # from news_sentiment

    # Final
    report:         str     # final synthesized report
    charts:         dict    # NEW! chart figures
    status:         str     # "running" / "complete" / "error"
    error:          str


# ── Node Functions ────────────────────────────────────────────

def node_detect_and_fetch(state: CryptoState) -> dict:
    """
    Node 1: Detect coin from query, fetch live price data.
    """
    symbol     = detect_coin(state["query"])
    price_data = run_price_fetcher(symbol)

    return {
        "symbol":     symbol,
        "price_data": price_data,
        "status":     "analyzing",
    }


def node_run_agents_parallel(state: CryptoState) -> dict:
    """
    Node 2: Run Market Analyst and News Sentiment in PARALLEL.

    Both agents only need price_data — they don't depend on each other.
    Running in parallel: ~2× faster than sequential.
    """
    price_data = state["price_data"]

    market_data    = {}
    sentiment_data = {}

    print("🚀 Running Market Analyst + News Sentiment in parallel...")

    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = {
            executor.submit(run_market_analyst, price_data): "market",
            executor.submit(run_news_sentiment, price_data): "sentiment",
        }
        for future in as_completed(futures):
            name = futures[future]
            try:
                result = future.result()
                if name == "market":
                    market_data = result
                else:
                    sentiment_data = result
            except Exception as e:
                print(f"  ⚠️  Agent '{name}' failed: {e}")
                if name == "market":
                    market_data    = {"agent": "Market Analyst", "analysis": f"Failed: {e}", "success": False}
                else:
                    sentiment_data = {"agent": "News Sentiment", "sentiment": f"Failed: {e}", "sentiment_score": 5, "sentiment_label": "Neutral", "success": False}

    return {
        "market_data":    market_data,
        "sentiment_data": sentiment_data,
        "status":         "writing_report",
    }


def node_write_report(state: CryptoState) -> dict:
    """Node 3: Synthesize all findings into final report."""
    result = run_report_writer(
        price_data     = state["price_data"],
        market_data    = state["market_data"],
        sentiment_data = state["sentiment_data"],
    )
    return {
        "report": result["report"],
        "status": "generating_charts",
    }


def node_generate_charts(state: CryptoState) -> dict:
    """Node 4 (NEW): Generate interactive charts from price data."""
    try:
        print("📊 Generating interactive charts...")
        result = run_chart_generator(
            symbol=state["symbol"],
            price_data=state["price_data"]
        )
        return {
            "charts": result.get("charts", {}),
            "status": "complete",
        }
    except Exception as e:
        print(f"⚠️  Chart generation failed: {e}")
        return {
            "charts": {},
            "status": "complete",
        }


# ── Build Graph ───────────────────────────────────────────────

def build_graph():
    graph = StateGraph(CryptoState)

    graph.add_node("fetch_price",    node_detect_and_fetch)
    graph.add_node("run_agents",     node_run_agents_parallel)
    graph.add_node("write_report",   node_write_report)
    graph.add_node("gen_charts",     node_generate_charts)

    graph.set_entry_point("fetch_price")
    graph.add_edge("fetch_price",  "run_agents")
    graph.add_edge("run_agents",   "write_report")
    graph.add_edge("write_report", "gen_charts")
    graph.add_edge("gen_charts",   END)

    return graph.compile()


# ── Main Entry Point ──────────────────────────────────────────

def analyze_crypto(query: str) -> dict:
    """
    Main function — analyze a crypto query end to end.

    Args:
        query: user question e.g. "What is Bitcoin doing today?"

    Returns:
        Final state with report, price_data, sentiment etc.
    """
    if not query or not query.strip():
        return {
            "report": "Please ask a question about a cryptocurrency.",
            "status": "error",
        }

    graph = build_graph()

    initial_state: CryptoState = {
        "query":          query,
        "symbol":         "",
        "price_data":     {},
        "market_data":    {},
        "sentiment_data": {},
        "report":         "",
        "charts":         {},
        "status":         "starting",
        "error":          "",
    }

    try:
        return graph.invoke(initial_state)
    except Exception as e:
        return {
            "report": f"❌ Analysis failed: {str(e)}",
            "status": "error",
            "error":  str(e),
        }