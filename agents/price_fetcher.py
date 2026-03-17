# ============================================================
# agents/price_fetcher.py — Live price data from Binance
# ============================================================
# ONE job: fetch live price + 24h stats from Binance API
# and return structured data for other agents to use.

from tools.binance_tools import (
    get_ticker_24h, get_klines,
    calculate_rsi, calculate_sma,
    format_price, format_volume,
    SUPPORTED_COINS,
)


def run_price_fetcher(symbol: str) -> dict:
    """
    Fetch live price data for a coin from Binance.

    Returns structured price data including:
    - Current price, 24h change, high/low
    - RSI (overbought/oversold indicator)
    - SMA7 and SMA25 (trend indicators)
    - Volume

    Args:
        symbol: coin symbol e.g. "BTC", "ETH"

    Returns:
        dict with all price data + formatted strings
    """
    print(f"  🔴 Price Fetcher: fetching {symbol}/USDT from Binance...")

    # ── Fetch 24h ticker
    ticker = get_ticker_24h(symbol)

    if not ticker.get("success"):
        return {
            "agent":   "Price Fetcher",
            "symbol":  symbol,
            "success": False,
            "error":   ticker.get("error", "Failed to fetch price"),
        }

    # ── Fetch 24 hourly candles for technical indicators
    klines = get_klines(symbol, interval="1h", limit=30)
    closes = [k["close"] for k in klines] if klines else []

    # ── Calculate indicators
    rsi   = calculate_rsi(closes) if len(closes) >= 15 else None
    sma7  = calculate_sma(closes, 7)  if len(closes) >= 7  else None
    sma25 = calculate_sma(closes, 25) if len(closes) >= 25 else None

    # ── Trend direction
    trend = "neutral"
    if sma7 and sma25:
        if sma7 > sma25:
            trend = "bullish"    # short-term average above long-term = uptrend
        elif sma7 < sma25:
            trend = "bearish"    # short-term average below long-term = downtrend

    # ── RSI signal
    rsi_signal = "neutral"
    if rsi:
        if rsi > 70:
            rsi_signal = "overbought"
        elif rsi < 30:
            rsi_signal = "oversold"

    # ── Change direction emoji
    change_emoji = "🟢" if ticker["change_pct"] >= 0 else "🔴"

    result = {
        "agent":        "Price Fetcher",
        "symbol":       symbol,
        "name":         SUPPORTED_COINS.get(symbol, symbol),
        "success":      True,

        # Raw numbers (for other agents to use)
        "price":        ticker["price"],
        "change_pct":   ticker["change_pct"],
        "change":       ticker["change"],
        "high_24h":     ticker["high"],
        "low_24h":      ticker["low"],
        "volume":       ticker["volume"],
        "quote_volume": ticker["quote_volume"],
        "trades":       ticker["trades"],
        "rsi":          rsi,
        "sma7":         sma7,
        "sma25":        sma25,
        "trend":        trend,
        "rsi_signal":   rsi_signal,

        # Formatted strings (for display)
        "price_fmt":    format_price(ticker["price"]),
        "high_fmt":     format_price(ticker["high"]),
        "low_fmt":      format_price(ticker["low"]),
        "volume_fmt":   format_volume(ticker["quote_volume"]),
        "change_emoji": change_emoji,
    }

    print(f"     ✅ {symbol}: {result['price_fmt']} ({ticker['change_pct']:+.2f}%)")
    return result
