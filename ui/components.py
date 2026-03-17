# ============================================================
# ui/components.py — Reusable HTML components
# ============================================================

import streamlit as st
from config import APP_TITLE, APP_SUBTITLE


def hero():
    st.markdown(f"""
    <div class="hero">
      <h1>{APP_TITLE}</h1>
      <p>{APP_SUBTITLE}</p>
    </div>
    """, unsafe_allow_html=True)


def market_ticker(prices: dict):
    """Show live prices for top coins in a ticker bar."""
    if not prices:
        return
    items = ""
    for symbol, price in list(prices.items())[:8]:
        fmt = f"${price:,.2f}" if price >= 1 else f"${price:.4f}"
        items += f'<span class="ticker-item"><span class="ticker-symbol">{symbol}</span>{fmt}</span>'
    st.markdown(f"""
    <div style='margin-bottom:4px;font-size:.66rem;color:#475569;text-transform:uppercase;letter-spacing:.1em'>
      <span class="live-dot"></span>Live Prices
    </div>
    <div class="market-ticker">{items}</div>
    """, unsafe_allow_html=True)


def price_display(price_data: dict):
    """Show the main price card."""
    if not price_data.get("success"):
        st.error(f"Could not fetch price: {price_data.get('error', 'Unknown error')}")
        return

    change     = price_data["change_pct"]
    change_cls = "price-change-up" if change >= 0 else "price-change-down"
    sign       = "+" if change >= 0 else ""

    st.markdown(f"""
    <div class="card">
      <div class="card-title">💰 Live Price — {price_data['name']} ({price_data['symbol']}/USDT)</div>
      <div class="price-big">{price_data['price_fmt']}</div>
      <div class="{change_cls}" style="margin-top:6px">{sign}{change:.2f}% (24h)</div>
      <div class="coin-name">High: {price_data['high_fmt']}  ·  Low: {price_data['low_fmt']}  ·  Vol: {price_data['volume_fmt']}</div>
    </div>
    """, unsafe_allow_html=True)


def stats_row(price_data: dict):
    """Show RSI, trend, trades stats."""
    rsi    = price_data.get("rsi")
    trend  = price_data.get("trend", "neutral").capitalize()
    trades = price_data.get("trades", 0)

    rsi_str = f"{rsi:.1f}" if rsi else "N/A"
    trend_emoji = "📈" if trend == "Bullish" else "📉" if trend == "Bearish" else "➡️"

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f'<div class="stat-box"><div class="stat-num">{rsi_str}</div><div class="stat-label">RSI (14)</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="stat-box"><div class="stat-num">{trend_emoji}</div><div class="stat-label">Trend — {trend}</div></div>', unsafe_allow_html=True)
    with c3:
        trades_fmt = f"{trades/1000:.1f}K" if trades >= 1000 else str(trades)
        st.markdown(f'<div class="stat-box"><div class="stat-num">{trades_fmt}</div><div class="stat-label">24h Trades</div></div>', unsafe_allow_html=True)


def sentiment_badge(sentiment_data: dict):
    """Show sentiment badge."""
    label = sentiment_data.get("sentiment_label", "Neutral 🟡")
    score = sentiment_data.get("sentiment_score", 5)
    cls   = "sentiment-bullish" if "Bullish" in label else "sentiment-bearish" if "Bearish" in label else "sentiment-neutral"
    st.markdown(f'<div class="sentiment-badge {cls}">Sentiment: {label} &nbsp;·&nbsp; Score: {score}/10</div>', unsafe_allow_html=True)


def report_box(text: str):
    """Render the final report."""
    import re
    # Convert markdown headers to styled HTML
    text = re.sub(r'## (.+)', r'<h2>\1</h2>', text)
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = text.replace('\n', '<br>')
    st.markdown(f'<div class="report-box">{text}</div>', unsafe_allow_html=True)


def empty_state():
    st.markdown("""
    <div style='text-align:center;padding:60px 20px;color:#1e293b'>
      <div style='font-size:3rem;margin-bottom:12px'>🪙</div>
      <div style='font-size:1rem;color:#475569;font-weight:600'>Ask anything about crypto</div>
      <div style='font-size:.82rem;color:#334155;margin-top:6px'>
        Try: "What is Bitcoin doing today?" or "Is ETH bullish?"
      </div>
    </div>
    """, unsafe_allow_html=True)


def card_open(title=""):
    st.markdown(f'<div class="card">{"<div class=card-title>" + title + "</div>" if title else ""}', unsafe_allow_html=True)


def card_close():
    st.markdown('</div>', unsafe_allow_html=True)
