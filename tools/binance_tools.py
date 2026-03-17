# ============================================================
# tools/binance_tools.py — Binance API + shared utilities
# ============================================================
# This file has ONE job: fetch live data from Binance public API
# and provide the LLM factory used by all agents.
#
# Binance public endpoints used (no API key needed):
#   /api/v3/ticker/24hr   → 24h price stats
#   /api/v3/ticker/price  → current price
#   /api/v3/klines        → candlestick/OHLC data

import re
import requests
from config import (
    BINANCE_BASE_URL, SUPPORTED_COINS, QUOTE_CURRENCY,
    GROQ_API_KEY, GROQ_MODEL, TEMPERATURE, MAX_TOKENS,
)


# ── LLM Factory ──────────────────────────────────────────────

def get_llm(temperature: float = TEMPERATURE):
    """
    Returns Groq LLM. All agents call this.
    """
    from langchain_groq import ChatGroq
    return ChatGroq(
        model=GROQ_MODEL,
        groq_api_key=GROQ_API_KEY,
        temperature=temperature,
        max_tokens=MAX_TOKENS,
    )


def clean_output(text) -> str:
    """Strip markdown fences from LLM output."""
    if hasattr(text, "content"):
        text = text.content
    return re.sub(r"```(?:\w+)?|```", "", str(text)).strip()


# ── Coin Detection ────────────────────────────────────────────

def detect_coin(query: str) -> str:
    """
    Extract coin symbol from user query.

    Handles:
      "What is the Bitcoin price?"  → "BTC"
      "How is ETH doing?"           → "ETH"
      "Tell me about BNB"           → "BNB"
      "Solana price"                → "SOL"
    """
    query_upper = query.upper()

    # Check direct symbol match first (BTC, ETH, etc.)
    for symbol in SUPPORTED_COINS:
        if symbol in query_upper:
            return symbol

    # Check full name match
    for symbol, name in SUPPORTED_COINS.items():
        if name.upper() in query_upper:
            return symbol

    # Common aliases
    aliases = {
        "BITCOIN":    "BTC",
        "ETHEREUM":   "ETH",
        "BINANCE":    "BNB",
        "SOLANA":     "SOL",
        "DOGECOIN":   "DOGE",
        "POLYGON":    "MATIC",
        "CHAINLINK":  "LINK",
        "LITECOIN":   "LTC",
        "AVALANCHE":  "AVAX",
    }
    for alias, symbol in aliases.items():
        if alias in query_upper:
            return symbol

    return "BTC"   # default to Bitcoin if nothing detected


# ── Binance API Calls ─────────────────────────────────────────

def get_ticker_24h(symbol: str) -> dict:
    """
    Fetch 24-hour price statistics from Binance.

    Returns dict with:
      price, change_pct, high, low, volume, open_price
    """
    pair = f"{symbol}{QUOTE_CURRENCY}"
    url  = f"{BINANCE_BASE_URL}/api/v3/ticker/24hr"

    try:
        resp = requests.get(url, params={"symbol": pair}, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        return {
            "symbol":      symbol,
            "pair":        pair,
            "price":       float(data["lastPrice"]),
            "open_price":  float(data["openPrice"]),
            "high":        float(data["highPrice"]),
            "low":         float(data["lowPrice"]),
            "change":      float(data["priceChange"]),
            "change_pct":  float(data["priceChangePercent"]),
            "volume":      float(data["volume"]),
            "quote_volume":float(data["quoteVolume"]),
            "trades":      int(data["count"]),
            "success":     True,
        }
    except Exception as e:
        return {"symbol": symbol, "success": False, "error": str(e)}


def get_klines(symbol: str, interval: str = "1h", limit: int = 24) -> list:
    """
    Fetch candlestick (OHLC) data from Binance.

    interval: "1m", "5m", "15m", "1h", "4h", "1d"
    limit: number of candles (max 1000)

    Returns list of dicts with open, high, low, close, volume.
    """
    pair = f"{symbol}{QUOTE_CURRENCY}"
    url  = f"{BINANCE_BASE_URL}/api/v3/klines"

    try:
        resp = requests.get(url, params={
            "symbol":   pair,
            "interval": interval,
            "limit":    limit,
        }, timeout=10)
        resp.raise_for_status()
        raw = resp.json()

        return [
            {
                "open":   float(c[1]),
                "high":   float(c[2]),
                "low":    float(c[3]),
                "close":  float(c[4]),
                "volume": float(c[5]),
            }
            for c in raw
        ]
    except Exception as e:
        return []


def get_multiple_prices(symbols: list) -> dict:
    """
    Fetch current prices for multiple coins at once.
    Used for the market overview panel.
    """
    url = f"{BINANCE_BASE_URL}/api/v3/ticker/price"
    results = {}

    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        all_prices = {item["symbol"]: float(item["price"]) for item in resp.json()}

        for symbol in symbols:
            pair = f"{symbol}{QUOTE_CURRENCY}"
            if pair in all_prices:
                results[symbol] = all_prices[pair]
    except Exception as e:
        pass

    return results


# ── Technical Indicators ──────────────────────────────────────

def calculate_rsi(closes: list, period: int = 14) -> float:
    """
    Calculate RSI (Relative Strength Index).

    RSI > 70 = overbought (possible price drop)
    RSI < 30 = oversold (possible price rise)
    RSI 40-60 = neutral
    """
    if len(closes) < period + 1:
        return 50.0   # neutral if not enough data

    gains, losses = [], []
    for i in range(1, len(closes)):
        diff = closes[i] - closes[i - 1]
        gains.append(max(diff, 0))
        losses.append(max(-diff, 0))

    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period

    if avg_loss == 0:
        return 100.0

    rs  = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return round(rsi, 2)


def calculate_sma(closes: list, period: int) -> float:
    """Simple Moving Average."""
    if len(closes) < period:
        return closes[-1] if closes else 0
    return round(sum(closes[-period:]) / period, 4)


def format_price(price: float) -> str:
    """Format price nicely — handles both large and small values."""
    if price >= 1000:
        return f"${price:,.2f}"
    elif price >= 1:
        return f"${price:.4f}"
    else:
        return f"${price:.6f}"


def format_volume(volume: float) -> str:
    """Format large volume numbers."""
    if volume >= 1_000_000_000:
        return f"${volume/1_000_000_000:.2f}B"
    elif volume >= 1_000_000:
        return f"${volume/1_000_000:.2f}M"
    elif volume >= 1_000:
        return f"${volume/1_000:.2f}K"
    return f"${volume:.2f}"
