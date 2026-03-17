# ============================================================
# agents/news_sentiment.py — News & sentiment analysis
# ============================================================
# ONE job: analyze recent news sentiment for a coin using
# the LLM's knowledge of recent crypto events and trends.
#
# Note: Uses LLM knowledge base for news — no external news
# API needed. For production, integrate CoinGecko news API
# or CryptoPanic API for real-time news.

from tools.binance_tools import get_llm, clean_output


SENTIMENT_PROMPT = """You are a cryptocurrency news and sentiment analyst.

Analyze the current market sentiment for {name} ({symbol}) based on:
- Recent developments in the {name} ecosystem
- Current market conditions and crypto market trends
- Community sentiment and social media activity
- Recent technical upgrades, partnerships, or issues
- Regulatory news affecting {name}

Price context: {name} is currently at {price_fmt} with a {change_pct:+.2f}% change in the last 24 hours.

Provide a sentiment analysis covering:

1. OVERALL SENTIMENT — Is the current sentiment Bullish, Bearish, or Neutral? Explain why.
2. KEY POSITIVE FACTORS — What positive developments support {name} right now?
3. KEY RISK FACTORS — What negative factors or risks should investors be aware of?
4. COMMUNITY MOOD — How is the broader crypto community feeling about {name}?
5. SENTIMENT SCORE — Give a sentiment score from 1 (very bearish) to 10 (very bullish) with reasoning.

Be honest and balanced. Mention both positives and negatives."""


def run_news_sentiment(price_data: dict) -> dict:
    """
    Run news and sentiment analysis for a coin.

    Args:
        price_data: output from run_price_fetcher()

    Returns:
        dict with sentiment analysis and score
    """
    if not price_data.get("success"):
        return {
            "agent":           "News Sentiment",
            "sentiment":       "Could not analyze — price data unavailable.",
            "sentiment_score": 5,
            "sentiment_label": "Neutral",
            "success":         False,
        }

    symbol = price_data["symbol"]
    name   = price_data["name"]
    print(f"  📰 News Sentiment: analyzing {symbol} sentiment...")

    llm    = get_llm(temperature=0.3)
    prompt = SENTIMENT_PROMPT.format(
        name       = name,
        symbol     = symbol,
        price_fmt  = price_data["price_fmt"],
        change_pct = price_data["change_pct"],
    )

    raw       = llm.invoke(prompt)
    sentiment = clean_output(raw)

    # Extract sentiment score from text (look for "score: X" pattern)
    import re
    score_match = re.search(r'(?:score|rating)[:\s]+(\d+)', sentiment, re.IGNORECASE)
    score = int(score_match.group(1)) if score_match else 5
    score = max(1, min(10, score))   # clamp to 1-10

    # Determine label
    if score >= 7:
        label = "Bullish 🟢"
    elif score <= 4:
        label = "Bearish 🔴"
    else:
        label = "Neutral 🟡"

    print(f"     ✅ Sentiment: {label} (score: {score}/10)")
    return {
        "agent":           "News Sentiment",
        "sentiment":       sentiment,
        "sentiment_score": score,
        "sentiment_label": label,
        "success":         True,
    }
