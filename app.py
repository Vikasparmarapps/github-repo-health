# ============================================================
# app.py — Streamlit UI
# ============================================================
# Run: streamlit run app.py

import os
import streamlit as st

os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
os.environ["TF_CPP_MIN_LOG_LEVEL"]  = "3"

from config               import SUPPORTED_COINS
from graph.workflow       import analyze_crypto
from tools.binance_tools  import get_multiple_prices
from ui.styles            import load_css
from ui.components        import (
    hero, market_ticker, price_display,
    stats_row, sentiment_badge, report_box,
    empty_state, card_open, card_close,
)

# ════════════════════════════════════════════
# PAGE CONFIG
# ════════════════════════════════════════════
st.set_page_config(
    page_title="Binance AI Agent",
    page_icon="🪙",
    layout="wide",
    initial_sidebar_state="collapsed",
)

load_css()

# ════════════════════════════════════════════
# SESSION STATE
# ════════════════════════════════════════════
for key, default in [
    ("result", None),
    ("query",  ""),
]:
    if key not in st.session_state:
        st.session_state[key] = default

# ════════════════════════════════════════════
# LIVE MARKET TICKER
# ════════════════════════════════════════════
hero()

try:
    live_prices = get_multiple_prices(list(SUPPORTED_COINS.keys())[:8])
    market_ticker(live_prices)
except Exception:
    pass

# ════════════════════════════════════════════
# LAYOUT
# ════════════════════════════════════════════
col_left, col_right = st.columns([1, 1.2], gap="large")

# ── LEFT: Input
with col_left:
    card_open("💬 Ask About Any Crypto")

    # Quick question buttons
    st.markdown("<div style='color:#475569;font-size:.75rem;margin-bottom:8px'>Quick questions:</div>", unsafe_allow_html=True)
    qcols = st.columns(2)
    quick_qs = [
        "Show BTC chart",
        "Display Ethereum trend",
        "Show SOL analysis",
        "Analyze BNB with charts",
    ]
    for i, q in enumerate(quick_qs):
        with qcols[i % 2]:
            if st.button(q, key=f"quick_{i}", use_container_width=True):
                st.session_state.query = q
                st.session_state.auto_analyze = True
                st.rerun()

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    query = st.text_input(
        "question",
        value=st.session_state.query,
        placeholder="e.g. What is the Bitcoin price? Is ETH going up?",
        label_visibility="collapsed",
        key="query_input",
    )

    analyze_btn = st.button("🔍 Analyze", use_container_width=True)
    card_close()

    # Agent pipeline info
    card_open("🤖 Agent Pipeline")
    st.markdown("""
    <div style='display:flex;flex-direction:column;gap:8px'>
      <div style='display:flex;align-items:center;gap:10px'>
        <span style='color:#F0B90B;font-size:1rem'>1</span>
        <span style='color:#94a3b8;font-size:.82rem'>🔴 <b>Price Fetcher</b> — live data from Binance API</span>
      </div>
      <div style='display:flex;align-items:center;gap:10px'>
        <span style='color:#F0B90B;font-size:1rem'>2</span>
        <span style='color:#94a3b8;font-size:.82rem'>📊 <b>Market Analyst</b> + 📰 <b>News Sentiment</b> — parallel</span>
      </div>
      <div style='display:flex;align-items:center;gap:10px'>
        <span style='color:#F0B90B;font-size:1rem'>3</span>
        <span style='color:#94a3b8;font-size:.82rem'>📝 <b>Report Writer</b> — final synthesis</span>
      </div>
    </div>
    <div style='color:#334155;font-size:.74rem;margin-top:10px'>
      Powered by LangGraph · Groq · Binance Public API
    </div>
    """, unsafe_allow_html=True)
    card_close()

# ── RIGHT: Results
with col_right:

    # Check if analyze button clicked OR quick button was clicked
    trigger_analysis = analyze_btn or st.session_state.get("auto_analyze", False)
    
    if trigger_analysis:
        # Clear the auto_analyze flag
        st.session_state.auto_analyze = False
        
        q = query.strip()
        if not q:
            st.warning("Please enter a question.")
        else:
            st.session_state.query = q
            with st.spinner("🤖 Fetching live data and analyzing..."):
                result = analyze_crypto(q)
                st.session_state.result = result

    if st.session_state.result:
        result = st.session_state.result

        if result.get("status") == "error":
            st.error(result.get("report", "Analysis failed."))
        else:
            price_data     = result.get("price_data", {})
            sentiment_data = result.get("sentiment_data", {})

            # Price card
            price_display(price_data)

            # Stats row
            if price_data.get("success"):
                stats_row(price_data)
                st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

            # Sentiment badge
            if sentiment_data.get("success"):
                sentiment_badge(sentiment_data)

            # ── NEW: Charts Section ──
            charts = result.get("charts", {})
            if charts and len(charts) > 0:
                st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
                st.markdown("### 📈 Interactive Charts")
                
                chart_tabs = st.tabs([
                    "🕯️ Candlestick",
                    "📊 Price Trend",
                    "🔧 RSI Indicator",
                    "📉 Volume"
                ])
                
                with chart_tabs[0]:
                    if "candlestick" in charts:
                        st.plotly_chart(charts["candlestick"], use_container_width=True)
                    else:
                        st.info("Candlestick chart not available")
                
                with chart_tabs[1]:
                    if "trend" in charts:
                        st.plotly_chart(charts["trend"], use_container_width=True)
                    else:
                        st.info("Trend chart not available")
                
                with chart_tabs[2]:
                    if "rsi" in charts:
                        st.plotly_chart(charts["rsi"], use_container_width=True)
                    else:
                        st.info("RSI chart not available")
                
                with chart_tabs[3]:
                    if "volume" in charts:
                        st.plotly_chart(charts["volume"], use_container_width=True)
                    else:
                        st.info("Volume chart not available")

            # Tabbed results
            st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
            tab_report, tab_technical, tab_sentiment = st.tabs([
                "📋 Full Report",
                "📊 Technical Analysis",
                "📰 News & Sentiment",
            ])

            with tab_report:
                report_box(result.get("report", "No report available."))
                st.download_button(
                    "⬇️ Download Report (.txt)",
                    data=result.get("report", "").encode(),
                    file_name=f"{price_data.get('symbol', 'crypto')}_analysis.txt",
                    mime="text/plain",
                )

            with tab_technical:
                analysis = result.get("market_data", {}).get("analysis", "No analysis.")
                report_box(analysis)

            with tab_sentiment:
                sentiment = result.get("sentiment_data", {}).get("sentiment", "No sentiment data.")
                report_box(sentiment)
    else:
        empty_state()