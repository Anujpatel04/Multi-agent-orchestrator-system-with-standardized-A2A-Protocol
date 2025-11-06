# Quick Deployment Guide

## 🚀 Push to GitHub (Ready Now!)

Your code is committed and ready to push. Run:

```bash
git push -u origin main
```

If you need authentication:
- Use GitHub Personal Access Token (GitHub Settings → Developer settings → Personal access tokens)
- Or configure SSH: `git remote set-url origin git@github.com:Anujpatel04/Multi-agent-orchestrator-system-with-standardized-A2A-Protocol.git`

## 🌐 Deploy Options

### Option 1: Railway (Easiest - Free Tier Available)

1. **Connect GitHub**:
   - Go to [railway.app](https://railway.app)
   - Sign in with GitHub
   - New Project → Deploy from GitHub repo
   - Select your repository

2. **Configure**:
   - Railway auto-detects Python/Flask
   - Add environment variable: `GEMINI_API_KEY` = your key
   - Add: `PORT` = 5001 (or leave default)

3. **Deploy**: Automatic! Railway will deploy on every push.

### Option 2: Render (Free Tier)

1. **Connect Repository**:
   - Go to [render.com](https://render.com)
   - Sign in with GitHub
   - New → Web Service
   - Connect: `Anujpatel04/Multi-agent-orchestrator-system-with-standardized-A2A-Protocol`

2. **Settings**:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python web_app.py`
   - **Environment**: Python 3
   - **Environment Variables**: Add `GEMINI_API_KEY`

3. **Deploy**: Click "Create Web Service"

### Option 3: Heroku (Free Tier Discontinued, Paid)

1. **Install Heroku CLI**:
   ```bash
   brew install heroku/brew/heroku
   heroku login
   ```

2. **Create and Deploy**:
   ```bash
   heroku create your-app-name
   git push heroku main
   heroku config:set GEMINI_API_KEY=your_key
   heroku open
   ```

### Option 4: Vercel (Alternative)

1. **Install Vercel CLI**:
   ```bash
   npm i -g vercel
   vercel login
   ```

2. **Deploy**:
   ```bash
   vercel
   ```

## 📋 Environment Variables

All platforms need:
- `GEMINI_API_KEY`: Your Google Gemini API key
- `PORT`: (Optional, defaults to 5001)

## ✅ After Deployment

1. Visit your app URL
2. Test the chat interface
3. Check agent status
4. Monitor logs for any issues

## 🔄 Auto-Deploy on Git Push

**Railway & Render** support automatic deployments:
- Every push to `main` branch triggers automatic deployment
- No manual deployment needed after initial setup

## 📝 Notes

- Vector databases are created on first run (no setup needed)
- Free tier rate limits: 2 requests/minute for Gemini API
- App will be accessible at: `https://your-app-name.railway.app` (or similar)

