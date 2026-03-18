# ============================================================
# ui/styles.py — CSS loader
# ============================================================

import streamlit as st


_CSS = """
section[data-testid="stSidebar"] { display: none !important; }
#MainMenu, footer, header { display: none !important; }
.stApp { background: #060a0f; }
.block-container { max-width: 1100px !important; padding: 0 28px 80px !important; }
html, body { font-family: 'Inter', sans-serif; color: #e2e8f0; }

.hero { text-align: center; padding: 40px 0 20px; }
.hero h1 { font-size: 2rem; font-weight: 700; background: linear-gradient(135deg, #F0B90B 0%, #F8D12F 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin: 0 0 6px; }
.hero p { color: #475569; font-size: .88rem; margin: 0; }

.card { background: #0c1420; border: 1px solid #1e293b; border-radius: 14px; padding: 18px 22px; margin-bottom: 14px; }
.card-title { font-size: .66rem; font-weight: 700; letter-spacing: .12em; color: #F0B90B; text-transform: uppercase; margin-bottom: 10px; }

.price-big { font-size: 2.4rem; font-weight: 700; font-family: 'JetBrains Mono', monospace; color: #f1f5f9; line-height: 1; }
.price-change-up { font-size: 1rem; font-weight: 600; color: #22c55e; }
.price-change-down { font-size: 1rem; font-weight: 600; color: #ef4444; }
.coin-name { font-size: .8rem; color: #64748b; margin-top: 4px; }

.stTextInput input { background: #071015 !important; border: 1.5px solid #1e293b !important; border-radius: 10px !important; color: #e2e8f0 !important; font-family: 'Inter', sans-serif !important; font-size: .9rem !important; }
.stTextInput input:focus { border-color: #F0B90B !important; box-shadow: 0 0 0 3px rgba(240,185,11,.08) !important; }
.stButton > button { background: linear-gradient(135deg, #F0B90B, #d4a017) !important; border: none !important; border-radius: 10px !important; color: #000 !important; font-family: 'Inter', sans-serif !important; font-weight: 700 !important; font-size: .9rem !important; padding: 11px 24px !important; transition: opacity .2s, transform .15s !important; width: 100% !important; }
.stButton > button:hover { opacity: .88 !important; transform: translateY(-1px) !important; }

.report-box { background: #071015; border: 1px solid #1e293b; border-radius: 12px; padding: 22px 26px; line-height: 1.9; color: #cbd5e1; font-size: .9rem; }
.report-box h2 { color: #F0B90B; font-size: 1rem; margin: 20px 0 8px; font-weight: 700; }

.market-ticker { display: flex; gap: 12px; flex-wrap: wrap; margin-bottom: 16px; }
.ticker-item { background: #0c1420; border: 1px solid #1e293b; border-radius: 8px; padding: 8px 14px; font-size: .8rem; font-family: 'JetBrains Mono', monospace; }
.ticker-symbol { color: #F0B90B; font-weight: 700; margin-right: 6px; }
.ticker-up { color: #22c55e; }
.ticker-down { color: #ef4444; }

.sentiment-badge { display: inline-flex; align-items: center; gap: 6px; border-radius: 20px; padding: 5px 14px; font-size: .8rem; font-weight: 600; margin-bottom: 12px; }
.sentiment-bullish { background: #052e16; border: 1px solid #22c55e; color: #22c55e; }
.sentiment-bearish { background: #2d0a0a; border: 1px solid #ef4444; color: #ef4444; }
.sentiment-neutral { background: #1a1500; border: 1px solid #F0B90B; color: #F0B90B; }

.stat-box { background: #071015; border: 1px solid #1e293b; border-radius: 10px; padding: 12px 16px; text-align: center; }
.stat-num { font-size: 1.3rem; font-weight: 700; color: #F0B90B; font-family: 'JetBrains Mono', monospace; }
.stat-label { font-size: .7rem; color: #64748b; margin-top: 2px; }

.stSpinner > div { border-top-color: #F0B90B !important; }

@keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: .4; } }
.live-dot { display: inline-block; width: 7px; height: 7px; background: #22c55e; border-radius: 50%; animation: pulse 1.5s infinite; margin-right: 6px; }

@keyframes bounce { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(5px); } }
"""

_FONTS = (
    "<link href='https://fonts.googleapis.com/css2"
    "?family=Inter:wght@300;400;500;600;700"
    "&family=JetBrains+Mono:wght@400;600"
    "&display=swap' rel='stylesheet'>"
)


def load_css():
    # st.html() injects raw HTML directly into the page — no sanitization, no iframe.
    # This is the only reliable way to inject <style> in Streamlit 1.32+
    st.html(f"{_FONTS}<style>{_CSS}</style>")