# ============================================================
# config.py — All settings. Change only this file.
# ============================================================

import os
from dotenv import load_dotenv

load_dotenv()

# ── Groq LLM
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
GROQ_MODEL   = "llama-3.1-8b-instant"   # fast + free
TEMPERATURE  = 0.2
MAX_TOKENS   = 1024
print(f"Using Groq model: {GROQ_API_KEY}")
# ── Binance API (public endpoints — no auth needed)
BINANCE_BASE_URL = "https://api.binance.com"

# ── Supported coins — symbol → full name
SUPPORTED_COINS = {
    "BTC":  "Bitcoin",
    "ETH":  "Ethereum",
    "BNB":  "Binance Coin",
    "SOL":  "Solana",
    "XRP":  "XRP",
    "ADA":  "Cardana",
    "DOGE": "Dogecoin",
    "AVAX": "Avalanche",
    "DOT":  "Polkadot",
    "MATIC":"Polygon",
    "LINK": "Chainlink",
    "UNI":  "Uniswap",
    "ATOM": "Cosmos",
    "LTC":  "Litecoin",
}

# Default quote currency
QUOTE_CURRENCY = "USDT"

# ── News search (using Groq's knowledge — no external API needed)
NEWS_LOOKBACK_DAYS = 7

# ── UI settings
APP_TITLE    = "🪙 Binance AI Agent"
APP_SUBTITLE = "Live crypto analysis powered by LangGraph · Groq · Binance API"

if GROQ_API_KEY:
    print(f"✅ Groq API key loaded — model: {GROQ_MODEL}")
else:
    print("❌ GROQ_API_KEY not set — add it to .env file")
