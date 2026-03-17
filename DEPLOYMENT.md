# 🚀 Deployment Guide - Binance AI Agent

Deploy your Binance AI Agent to Streamlit Cloud in 5 minutes!

---

## Prerequisites

- GitHub account (free)
- Streamlit Cloud account (free)
- Your project pushed to GitHub

---

## Step 1: Prepare Your Project

### Create `.streamlit/secrets.toml`

In your project root, create `.streamlit/secrets.toml`:

```toml
GROQ_API_KEY = "your_groq_api_key_here"
```

**Don't commit this file!** Add to `.gitignore`:

```
.streamlit/secrets.toml
```

### Update `requirements.txt`

Make sure it has all dependencies:

```
langgraph>=0.0.20
langchain>=0.1.0
groq>=0.4.0
streamlit>=1.28.0
plotly>=5.17.0
pandas>=2.0.0
numpy>=1.24.0
requests>=2.31.0
python-dotenv>=1.0.0
```

### Create `.gitignore`

```
.env
.env.local
.streamlit/secrets.toml
__pycache__/
*.pyc
.DS_Store
.cache/
.pytest_cache/
```

---

## Step 2: Push to GitHub

```bash
# Initialize git (if not already)
git init

# Add all files
git add .

# Commit
git commit -m "Add Binance AI Agent with charts"

# Create repo on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/binance_agent.git
git branch -M main
git push -u origin main
```

---

## Step 3: Deploy to Streamlit Cloud

### Go to Streamlit Cloud

1. Open https://streamlit.io/cloud
2. Click "Sign in" → Sign in with GitHub
3. Click "New app"

### Configure Deployment

1. **Repository:** Select your repo
   - Example: `Vikasparmarapps/binance_agent`

2. **Branch:** Select `main`

3. **Main file path:** Enter `app.py`

4. **App URL:** (Auto-generated)
   - Example: `binance-ai-agent.streamlit.app`

### Add Secrets

1. Click "Advanced settings"
2. Paste your `.streamlit/secrets.toml` content:

```toml
GROQ_API_KEY = "gsk_your_actual_key_here"
```

3. Click "Deploy"

---

## Step 4: Monitor Deployment

Streamlit will show:

```
🎈 Streamlit server is securely set up.
You can now view your Streamlit app in your browser.
URL: https://binance-ai-agent.streamlit.app
```

---

## Step 5: Test Live

1. Open your app URL
2. Click "Show BTC chart"
3. Wait for analysis
4. See charts! 📊

---

## After Deployment

### Update Your App

Push changes to GitHub:

```bash
git add .
git commit -m "Fix: quick buttons auto-trigger"
git push
```

Streamlit auto-deploys within 1 minute! ✨

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'plotly'"

**Fix:** Update `requirements.txt` and push:

```
plotly>=5.17.0
```

```bash
git add requirements.txt
git commit -m "Add plotly"
git push
```

### "API key error"

**Fix:** Check `.streamlit/secrets.toml` in Streamlit Cloud settings

1. Go to your app settings
2. Secrets section
3. Verify `GROQ_API_KEY` is set correctly

### Slow Performance

**Optimize:**
- Cache data with `@st.cache_data`
- Use smaller data limits
- Deploy to higher tier (if needed)

---

## Performance Tips

### 1. Cache Results

```python
@st.cache_data(ttl=300)
def get_price_data(symbol):
    return run_price_fetcher(symbol)
```

### 2. Optimize Charts

```python
# Use fewer data points for faster rendering
KLINES_LIMIT = 50  # Instead of 100
```

### 3. Monitor Resources

Visit your app's "Manage app" → "Logs" to see:
- Memory usage
- CPU usage
- API calls

---

## Sharing Your App

### Share Link

```
https://binance-ai-agent.streamlit.app
```

### Embed in Website

```html
<iframe 
  src="https://binance-ai-agent.streamlit.app?embedded=true" 
  height="600" 
  width="100%">
</iframe>
```

### Add to Portfolio

```markdown
## Binance AI Agent

🚀 Live Demo: [binance-ai-agent.streamlit.app](https://binance-ai-agent.streamlit.app)

AI-powered cryptocurrency analysis with interactive charts.

**Tech Stack:**
- LangGraph (agent orchestration)
- Groq LLaMA (LLM)
- Binance API (live data)
- Streamlit (web UI)
- Plotly (charts)

**Features:**
- Real-time price analysis
- Technical indicators
- Market sentiment
- Interactive charts
- 2.8s analysis time
```

---

## Continuous Deployment

### Auto-Deploy on Push

Streamlit Cloud automatically deploys when you push to GitHub!

```bash
# Make changes
git add .
git commit -m "Update app"
git push  # → Auto-deploys! ✨
```

### Roll Back to Previous Version

1. Go to Streamlit Cloud settings
2. Select previous deployment
3. Click "Restore"

---

## Production Checklist

- [ ] Requirements.txt updated with all dependencies
- [ ] .gitignore configured properly
- [ ] Secrets added to Streamlit Cloud
- [ ] App tested locally with `streamlit run app.py`
- [ ] No hardcoded API keys in code
- [ ] All imports working
- [ ] Charts displaying correctly
- [ ] Quick buttons triggering analysis
- [ ] No error messages in console
- [ ] Performance acceptable (<5 seconds)

---

## Support

### Streamlit Cloud Docs
https://docs.streamlit.io/streamlit-cloud

### Community Forum
https://discuss.streamlit.io

### Issues
Check your app logs: Manage app → Logs

---

## Your App is Live! 🎉

Congratulations! Your Binance AI Agent is now deployed and accessible worldwide!

Share with:
- Friends: Send app link
- Portfolio: Add to GitHub projects
- Social: Tweet/share your achievement

**Your URL:** `https://binance-ai-agent.streamlit.app` (example)

Happy deploying! 🚀📊
