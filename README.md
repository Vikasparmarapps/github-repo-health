# Binance AI Agent

An intelligent multi-agent cryptocurrency analysis system powered by **LangGraph**, **Groq LLM**, and **Binance Public API**. Four specialized agents work in parallel to deliver real-time market analysis, technical insights, and sentiment-based recommendations.

**Live Demo**: [Coming Soon - Streamlit Deployment]  
**Author**: Vikas Parmar (@vikasparmarapps) | **Email**: vikasparmar444@gmail.com  
**GitHub**: github.com/Vikasparmarapps/binance-agent  

---

## 🎯 Features

✨ **Multi-Agent Architecture**: 4 specialized agents orchestrated via LangGraph  
📊 **Live Market Data**: Real-time prices, volumes, and OHLC from Binance public API  
🔍 **Technical Analysis**: RSI, SMA, trend detection—100% automated  
💬 **AI-Powered Sentiment**: Market sentiment analysis via Groq LLM  
🚀 **Parallel Processing**: Agents 2 & 3 run concurrently (ThreadPoolExecutor)  
📈 **Synthesis Reports**: Agent 4 creates actionable final recommendations  
🔐 **Zero Secrets**: Public API only—no trading keys, maximum security  
⚙️ **Cursor-Ready**: Full `.cursorrules` configuration included  
🎛️ **Highly Configurable**: Change models, coins, settings in one file  

---

## 🏗️ Architecture

```
Streamlit UI (Query Input)
         ↓
    config.py (ALL settings live here)
         ↓
╔═══════════════════════════════════════════════════════════════╗
║           LangGraph StateGraph Workflow                       ║
╠═══════════════════════════════════════════════════════════════╣
║                                                              ║
║  Agent 1: Price Fetcher                                     ║
║  ├─ Binance /api/v3/ticker/24hr (current price, 24h stats) ║
║  ├─ Binance /api/v3/klines (candlestick OHLCV data)        ║
║  └─ Output: {price, volume, change%, high, low, open}      ║
║                 ↓                                            ║
║  ┌──────────────────────────────────────────────────────┐  ║
║  │ Agent 2: Market Analyst    Agent 3: Sentiment Analyst│  ║
║  │ (runs in PARALLEL via ThreadPoolExecutor)            │  ║
║  │                                                      │  ║
║  │ Agent 2:                   Agent 3:                  │  ║
║  │ ├─ RSI calculation          ├─ News sentiment       │  ║
║  │ ├─ SMA trends              ├─ LLM reasoning        │  ║
║  │ ├─ Signal: BUY/HOLD/SELL   ├─ Bullish/bearish     │  ║
║  │ └─ Confidence %            └─ Score: -1.0 to +1.0  │  ║
║  └──────────────────────────────────────────────────────┘  ║
║                 ↓                                            ║
║  Agent 4: Report Writer                                     ║
║  ├─ Synthesize all agent outputs                           ║
║  ├─ Generate narrative analysis                            ║
║  ├─ Reasoning: why BUY/SELL                                ║
║  └─ Output: final_report (Markdown)                        ║
║                 ↓                                            ║
║         Display in Streamlit UI                            ║
╚═══════════════════════════════════════════════════════════════╝
```

### Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Orchestration** | LangGraph (StateGraph) | Agent coordination & workflow |
| **LLM** | Groq (llama-3.1-8b-instant) | Fast inference, cost-efficient |
| **Market Data** | Binance Public API (REST) | Real-time crypto market data |
| **Frontend** | Streamlit | Interactive web UI |
| **Concurrency** | ThreadPoolExecutor | Parallel agent execution |
| **Data** | Pandas, NumPy | Technical indicators & analysis |

---

## 📁 Project Structure

```
binance-agent/
├── app.py                    # Streamlit UI entry point (logic-free)
├── config.py                 # ⭐ ALL settings live here
├── .cursorrules              # Cursor multi-agent configuration
├── .env.example              # Environment template
├── requirements.txt          # Python dependencies
│
├── graph/
│   └── workflow.py           # LangGraph StateGraph definition
│
├── agents/
│   ├── price_fetcher.py      # Agent 1: Fetch Binance data
│   ├── market_analyst.py     # Agent 2: Technical analysis (RSI, SMA)
│   ├── sentiment_analyst.py  # Agent 3: Sentiment analysis
│   └── report_writer.py      # Agent 4: Synthesize report
│
├── tools/
│   └── binance_tools.py      # Binance API calls + LLM factory
│
├── ui/
│   ├── styles.py             # CSS loader
│   └── components.py         # Reusable UI components
│
|── DEPLOYMENT.md
|
└── README.md
```

---

## 🚀 Quick Start

### Prerequisites
- **Python 3.9+**
- **Groq API key** (free: https://console.groq.com)
- **Internet connection** (Binance API access)

### Installation

1. **Clone repository**
```bash
git clone https://github.com/Vikasparmarapps/binance-agent.git
cd binance-agent
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate
# On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
```bash
cp .env.example .env
# Edit .env and add your Groq API key
nano .env
```

5. **Run application**
```bash
streamlit run app.py
```

Open your browser to `http://localhost:8501`

---

## 💻 Usage

### Basic Workflow

**Input**: Natural language query about a cryptocurrency
```
"Analyze BTC market conditions"
"What's the sentiment on Ethereum?"
"Should I watch Solana right now?"
```

**Processing**:
1. Extract coin symbol via `detect_coin()`
2. Agent 1 fetches live data from Binance
3. Agent 2 & 3 analyze in parallel
4. Agent 4 synthesizes final report

**Output**:
```
BTC/USDT Market Analysis
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 Price Data
Current: $65,432.50 (+2.34% in 24h)
24h High: $66,100.00 | Low: $64,200.00
Volume: 28.5B USDT

📈 Technical Analysis
RSI: 58.2 (Neutral zone)
SMA-20: $65,100 | SMA-50: $64,800
Trend: Slight uptrend with consolidation
Signal: HOLD (wait for breakout)

💬 Sentiment
Market Sentiment: Bullish
Confidence: 72%
Reasoning: Recent positive news, strong support levels

🎯 Final Recommendation
ACTION: HOLD / Watch for breakout above $66,000
RISK: Moderate | TIMEFRAME: 4-6 hours
```

### Supported Cryptocurrencies

Default: **BTC**, **ETH**, **BNB**, **SOL**

Add more in `config.py`:
```python
SUPPORTED_COINS = {
    "BTC": "Bitcoin",
    "ETH": "Ethereum",
    "XRP": "Ripple",  # Add any coin
}
```

---

## ⚙️ Configuration

All settings in one place: **`config.py`**

```python
# ===== LLM Settings =====
MODEL_NAME = "llama-3.1-8b-instant"
TEMPERATURE = 0.7

# ===== Binance API =====
BINANCE_BASE_URL = "https://api.binance.com"
TIMEFRAME = "1h"  # Candlestick interval

# ===== Coins =====
SUPPORTED_COINS = {
    "BTC": "Bitcoin",
    "ETH": "Ethereum",
    "BNB": "Binance Coin",
    "SOL": "Solana",
}

# ===== Technical Indicators =====
RSI_PERIOD = 14
SMA_SHORT = 20
SMA_LONG = 50
```

**Never hardcode settings**—edit only `config.py`.

---

## 🔧 How It Works

### Agent 1: Price Fetcher
Fetches live data from Binance public endpoints:
- `/api/v3/ticker/24hr` → Current price, 24h stats
- `/api/v3/klines` → OHLCV candlestick data (100 candles, 1h interval)

### Agent 2: Market Analyst
Analyzes technical indicators:
- RSI (Relative Strength Index) → Momentum (overbought/oversold)
- SMA (Simple Moving Averages) → Trend direction (20-period, 50-period)
- Signal generation: BUY (bullish), HOLD (neutral), SELL (bearish)

### Agent 3: Sentiment Analyst
Evaluates market sentiment via LLM reasoning:
- Price action analysis
- Volume strength assessment
- Market condition evaluation
- Bullish/bearish scoring (-1.0 to +1.0)

### Agent 4: Report Writer
Synthesizes all outputs into coherent analysis:
- Combines signals from Agents 1-3
- Creates narrative explanation
- Provides actionable recommendations
- Outputs Markdown-formatted report

---

## 🔐 Security

✅ **Public API Only**: Binance public endpoints (no auth)  
✅ **No Secrets in Code**: Groq API key in `.env`  
✅ **Environment Variables**: `.env` never committed  
✅ **Read-Only Operations**: Analysis only, no trading execution  
✅ **Input Validation**: Coin symbols validated against whitelist  

---

## 📊 Performance

| Metric | Value |
|--------|-------|
| **Total Execution Time** | 2-4 seconds |
| **Agent 1 (Price Fetch)** | 0.3-0.5s |
| **Agents 2+3 (Parallel)** | 1.5-2.5s combined |
| **Agent 4 (Synthesis)** | 0.5-1s |
| **Binance API Latency** | <500ms |
| **Groq LLM Inference** | ~1-2s per agent |
| **Rate Limit** | 1200 req/min (Binance public) |

See `PERFORMANCE.md` for detailed benchmarks and optimization notes.

---

## 🛠️ Development Conventions

### Never Do This ❌
```python
# Don't instantiate LLM in agents
from langchain_groq import ChatGroq
llm = ChatGroq(model_name="llama-3.1-8b-instant")

# Don't hardcode symbols
symbol = "BTCUSDT"

# Don't make Binance calls outside tools
requests.get("https://api.binance.com/...")

# Don't use inline CSS styles
st.markdown("<style>color: red;</style>")
```

### Always Do This ✅
```python
# Use LLM factory
from tools.binance_tools import get_llm
llm = get_llm()

# Use config
from config import SUPPORTED_COINS
symbol = f"{coin}USDT"

# Use tools module
from tools.binance_tools import fetch_binance_data
data = fetch_binance_data(symbol)

# Use styles.py
from ui.styles import load_styles
load_styles()
```

---

## 📚 Dependencies

See `requirements.txt`:
- **langgraph** - State machine orchestration
- **langchain** - LLM framework
- **groq** - LLM API client
- **streamlit** - Web UI
- **pandas** - Data analysis
- **numpy** - Numerical computing
- **requests** - HTTP requests
- **python-dotenv** - Environment variables

---

## 📧 Contact

**Author**: Vikas Parmar  
**Email**: vikasparmar444@gmail.com  
**GitHub**: @Vikasparmarapps  

---

**Built with ❤️ using LangGraph + Groq + Binance API**
