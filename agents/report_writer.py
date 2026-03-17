# ============================================================
# agents/report_writer.py — Final report synthesizer
# ============================================================
# ONE job: take outputs from all 3 agents and write a clean,
# plain-English summary with a clear verdict.

from tools.binance_tools import get_llm, clean_output


REPORT_PROMPT = """You are a senior crypto analyst writing a final report for an investor.

Synthesize the following analysis into one clear, actionable report.

=== PRICE DATA ===
Coin: {name} ({symbol})
Price: {price_fmt} ({change_pct:+.2f}% in 24h)
RSI: {rsi} — {rsi_signal}
Trend: {trend}

=== TECHNICAL ANALYSIS ===
{analysis}

=== NEWS & SENTIMENT ===
Sentiment: {sentiment_label} ({sentiment_score}/10)
{sentiment}

=== YOUR REPORT TASK ===
Write a structured report with these exact sections:

## 📊 Summary
One paragraph — the most important thing to know about {name} right now.

## ✅ Bullish Signals
2-3 bullet points of positive factors.

## ⚠️ Risk Factors
2-3 bullet points of risks or concerns.

## 🎯 Verdict
One clear sentence: is the current situation POSITIVE, NEGATIVE, or NEUTRAL for {name}?
Include a Confidence level: Low / Medium / High.

## 💡 What to Watch
2 specific things to monitor in the next 24-48 hours.

Keep it clear, factual, and accessible to a non-expert. No financial advice disclaimers needed."""


def run_report_writer(
    price_data:    dict,
    market_data:   dict,
    sentiment_data: dict,
) -> dict:
    """
    Synthesize all agent outputs into a final report.

    Args:
        price_data:     output from run_price_fetcher()
        market_data:    output from run_market_analyst()
        sentiment_data: output from run_news_sentiment()

    Returns:
        dict with final report text
    """
    print(f"  📝 Report Writer: synthesizing final report...")

    llm    = get_llm(temperature=0.2)
    prompt = REPORT_PROMPT.format(
        name             = price_data.get("name", "Unknown"),
        symbol           = price_data.get("symbol", ""),
        price_fmt        = price_data.get("price_fmt", "N/A"),
        change_pct       = price_data.get("change_pct", 0),
        rsi              = price_data.get("rsi", "N/A"),
        rsi_signal       = price_data.get("rsi_signal", "neutral").upper(),
        trend            = price_data.get("trend", "neutral").upper(),
        analysis         = market_data.get("analysis", "No analysis available."),
        sentiment_label  = sentiment_data.get("sentiment_label", "Neutral"),
        sentiment_score  = sentiment_data.get("sentiment_score", 5),
        sentiment        = sentiment_data.get("sentiment", "No sentiment data."),
    )

    raw    = llm.invoke(prompt)
    report = clean_output(raw)

    print(f"     ✅ Final report complete")
    return {
        "agent":  "Report Writer",
        "report": report,
        "success": True,
    }
