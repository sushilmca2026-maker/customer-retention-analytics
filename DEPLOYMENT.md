# Deploying to Streamlit Cloud

This repo is already structured the way Streamlit Community Cloud expects, so deployment is just
connecting the GitHub repo — no extra config files needed.

## Prerequisites

- Repo pushed to GitHub (public, or private on a plan that supports it)
- A free Streamlit Cloud account: https://share.streamlit.io (sign in with GitHub)

## Steps

1. **Push this repo to GitHub** (if you haven't already):
   ```bash
   cd customer-retention-analytics
   git remote add origin https://github.com/<your-username>/<repo-name>.git
   git branch -M main
   git push -u origin main
   ```

2. **Go to** https://share.streamlit.io **and click "New app".**

3. **Fill in the deploy form:**
   | Field | Value |
   |---|---|
   | Repository | `<your-username>/<repo-name>` |
   | Branch | `main` |
   | Main file path | `app/app.py` |
   | App URL (optional) | choose a custom slug, e.g. `customer-retention-analytics` |

4. **Click "Deploy."** Streamlit Cloud will:
   - Clone the repo
   - Install everything in `requirements.txt`
   - Launch `app/app.py`

   First deploy takes 2-5 minutes. You'll get a URL like:
   `https://customer-retention-analytics.streamlit.app`

## What Cloud picks up automatically

- **`requirements.txt`** at repo root — installed as-is, no changes needed.
- **`.streamlit/config.toml`** — your navy/gold theme is applied automatically; the `headless`
  setting is ignored on Cloud (harmless).
- **`data/Churn_Modelling.csv`** — bundled in the repo, so the dashboard has real data on first load
  with no extra setup. Users can still upload their own CSV from the sidebar to override it.

## Updating the live app

Streamlit Cloud auto-redeploys on every push to the connected branch. To update the live dashboard:
```bash
git add -A
git commit -m "Update analysis"
git push
```
The app restarts automatically (usually within ~1 minute).

## Managing secrets (not needed for this project)

This app doesn't use API keys or credentials, so there's nothing to add under
**App settings → Secrets**. If you later add a database connection or API integration, that's
where connection strings/keys would go (as TOML, injected as `st.secrets`).

## Resource limits (free tier)

- 1 GB RAM, sleeps after inactivity, wakes on next visit (~30-60s cold start)
- Fine for this project's scale (10,000 rows, no ML training at runtime)

## Common deploy issues

| Symptom | Fix |
|---|---|
| "ModuleNotFoundError" on deploy | Package missing from `requirements.txt` — add it and push |
| App shows old data after CSV update | Cloud caches with `@st.cache_data`; click the "Clear cache" option in the app's hamburger menu, or just wait for the next deploy |
| Build fails on matplotlib/seaborn | These are only used by `notebooks/eda_report.py`, not `app.py` — safe to remove from `requirements.txt` if you want a lighter/faster Cloud build (the dashboard itself only needs pandas, numpy, streamlit, plotly) |
