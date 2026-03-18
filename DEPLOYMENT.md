# Deployment Guide — GitHub Repo Health Monitor

---

## Local Development

```bash
# 1. Clone and enter project
git clone https://github.com/Vikasparmarapps/github-repo-health.git
cd github-repo-health

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
cp .env.example .env
# Open .env and add:
# GROQ_API_KEY=your_key_here
# GITHUB_TOKEN=your_token_here  (optional but recommended)

# 5. Run
streamlit run app.py
# Opens at http://localhost:8501
```

---

## Environment Variables

| Variable | Required | Where to get |
|---|---|---|
| `GROQ_API_KEY` | Yes | https://console.groq.com (free) |
| `GITHUB_TOKEN` | No | https://github.com/settings/tokens |

Without `GITHUB_TOKEN` the GitHub API allows 60 requests/hour.
With `GITHUB_TOKEN` the limit rises to 5,000 requests/hour.

To create a GitHub token: Settings → Developer settings → Personal access tokens → Tokens (classic) → Generate new token → select `public_repo` scope only.

---

## Streamlit Cloud Deployment (Free)

1. Push your code to GitHub (make sure `.env` is in `.gitignore`)
2. Go to https://share.streamlit.io
3. Click "New app"
4. Select your repository and set `app.py` as the main file
5. In "Advanced settings" → "Secrets", add:
```toml
GROQ_API_KEY = "your_groq_api_key_here"
GITHUB_TOKEN = "your_github_token_here"
```
6. Click Deploy

The app will be live at `https://yourname-reponame.streamlit.app`

---

## Railway Deployment

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway init
railway up
```

Add environment variables in the Railway dashboard under Variables.

---

## Docker (Optional)

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

```bash
docker build -t github-health .
docker run -p 8501:8501 \
  -e GROQ_API_KEY=your_key \
  -e GITHUB_TOKEN=your_token \
  github-health
```

---

## Troubleshooting

**`ModuleNotFoundError`**
```bash
pip install -r requirements.txt
```

**`GROQ_API_KEY not set`**
Make sure your `.env` file is in the same folder as `app.py` and contains `GROQ_API_KEY=your_key`.

**`GitHub API 403 rate limit`**
Add a `GITHUB_TOKEN` to your `.env` file. The public limit is 60 requests/hour; with a token it's 5,000/hour.

**`Repo not found`**
Make sure the repo is public and the format is `owner/repo` e.g. `langchain-ai/langchain`.

**CSS showing as raw text**
Make sure `ui/styles.py` uses `st.html()` not `st.markdown()` for CSS injection.