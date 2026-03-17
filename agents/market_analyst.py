# ============================================================
# agents/market_analyst.py — Technical market analysis
# ============================================================
# ONE job: take price data and generate a technical analysis
# using LLM with specific market context.

from tools.binance_tools import get_llm, clean_output


ANALYST_PROMPT = """You are an expert cryptocurrency market analyst.

Analyze the following live market data for {name} ({symbol}) and provide a clear technical analysis.

=== LIVE MARKET DATA ===
Current Price: {price_fmt}
24h Change: {change_pct:+.2f}% ({change_emoji})
24h High: {high_fmt}
24h Low: {low_fmt}
24h Trading Volume: {volume_fmt}
24h Trades: {trades:,}
RSI (14): {rsi}
SMA 7h: {sma7}
SMA 25h: {sma25}
Trend (SMA crossover): {trend}
RSI Signal: {rsi_signal}

=== YOUR ANALYSIS TASK ===
Write a concise technical analysis covering:

1. PRICE ACTION — What is the current price doing? Is momentum up or down?
2. TREND — What do the moving averages say about the trend direction?
3. RSI READING — Is the coin overbought, oversold, or neutral? What does this suggest?
4. VOLUME ANALYSIS — Is volume confirming the price move or diverging?
5. KEY LEVELS — What are the important support (low) and resistance (high) levels?
6. SHORT-TERM OUTLOOK — What does the data suggest for the next 24-48 hours?

Keep it factual and data-driven. 3-4 sentences per point. No financial advice."""


def run_market_analyst(price_data: dict) -> dict:
    """
    Run technical analysis on the price data.

    Args:
        price_data: output from run_price_fetcher()

    Returns:
        dict with analysis text
    """
    if not price_data.get("success"):
        return {
            "agent":    "Market Analyst",
            "analysis": "Could not analyze — price data unavailable.",
            "success":  False,
        }

    print(f"  📊 Market Analyst: analyzing {price_data['symbol']}...")

    llm    = get_llm(temperature=0.2)
    prompt = ANALYST_PROMPT.format(
        name       = price_data["name"],
        symbol     = price_data["symbol"],
        price_fmt  = price_data["price_fmt"],
        change_pct = price_data["change_pct"],
        change_emoji = price_data["change_emoji"],
        high_fmt   = price_data["high_fmt"],
        low_fmt    = price_data["low_fmt"],
        volume_fmt = price_data["volume_fmt"],
        trades     = price_data["trades"],
        rsi        = price_data.get("rsi", "N/A"),
        sma7       = price_data.get("sma7", "N/A"),
        sma25      = price_data.get("sma25", "N/A"),
        trend      = price_data.get("trend", "neutral").upper(),
        rsi_signal = price_data.get("rsi_signal", "neutral").upper(),
    )

    raw      = llm.invoke(prompt)
    analysis = clean_output(raw)

    print(f"     ✅ Market analysis complete")
    return {
        "agent":    "Market Analyst",
        "analysis": analysis,
        "success":  True,
    }
