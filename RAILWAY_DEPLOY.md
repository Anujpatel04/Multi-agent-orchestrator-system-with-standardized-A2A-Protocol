# Railway Deployment Guide

## Prerequisites
- Railway account (sign up at https://railway.app)
- GitHub repository with your code

## Deployment Steps

### 1. Connect Repository to Railway
1. Go to Railway dashboard
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose your repository

### 2. Configure Environment Variables
In Railway dashboard, go to your project → Variables tab and add:

```bash
# Required - Gemini API (for Agent 1)
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_API_KEY_AGENT1=your_gemini_api_key_here

# Required - DeepSeek API (for Orchestrator and Agent 2)
DEEPSEEK_API_KEY_ORCHESTRATOR=your_deepseek_api_key_here
DEEPSEEK_API_KEY=your_deepseek_api_key_here

# Optional - Flask settings
FLASK_DEBUG=False
PORT=5000  # Railway will set this automatically, but you can override
```

### 3. Railway Auto-Detection
Railway will automatically:
- Detect Python from `requirements.txt`
- Use the `Procfile` or `railway.json` for start command
- Set the `PORT` environment variable automatically
- Bind to `0.0.0.0` (already configured in code)

### 4. Build and Deploy
1. Railway will automatically build when you push to main branch
2. Or manually trigger deployment from Railway dashboard
3. Check logs in Railway dashboard for any errors

### 5. Access Your Application
- Railway will provide a public URL (e.g., `https://your-app.railway.app`)
- The app will be accessible at this URL
- Vector database will persist in Railway's filesystem

## Important Notes

### Vector Database Persistence
- Vector database is stored in `vector_db/` directory
- On Railway, this persists between deployments
- If you need to reset, delete the `vector_db/` directory in Railway's filesystem

### Environment Variables
- Never commit `.env` file to git (it's in `.gitignore`)
- Set all API keys in Railway dashboard → Variables
- Railway automatically provides `PORT` variable

### File Paths
- All paths are relative, so they work on Railway
- Vector database uses absolute paths that work on Railway

### Troubleshooting
- Check Railway logs if app doesn't start
- Verify all environment variables are set
- Ensure API keys are valid
- Check that port binding is correct (should be `0.0.0.0`)

## Quick Deploy Checklist
- [ ] Repository connected to Railway
- [ ] All environment variables set in Railway dashboard
- [ ] `requirements.txt` is up to date
- [ ] `Procfile` or `railway.json` exists (already present)
- [ ] Code pushed to main branch
- [ ] Railway deployment successful
- [ ] Application accessible via Railway URL

