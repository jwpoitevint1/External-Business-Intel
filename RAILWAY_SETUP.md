# Railway + Neon Setup (Step-by-Step)

## 1. Connect Repo to Railway
- Go to Railway
- New Project → Deploy from GitHub
- Select: External-Business-Intel

## 2. Add Environment Variable
In Railway → Variables:

DATABASE_URL=your_neon_connection_string

Example:
postgresql+psycopg://user:pass@host/db

## 3. Deploy
Railway will automatically:
- install requirements.txt
- use Procfile
- start FastAPI

## 4. Verify Deployment
Open your Railway URL:

/health

Expected:
{"status":"ok"}

## 5. Run First Scan

/trends/scan?query=social%20media%20marketing

## 6. What Happens
- Pulls public data (news + reddit)
- DeepSeek ETL normalizes + validates
- Qwen analyzes trends
- Returns structured intelligence

## 7. If It Fails
Check:
- DATABASE_URL is set
- Logs in Railway
- App started (uvicorn running)

## Done
You now have a live external intelligence system.
