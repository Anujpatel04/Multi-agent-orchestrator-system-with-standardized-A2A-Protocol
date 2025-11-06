# Deployment Guide

## Deployment Options

### Option 1: Railway (Recommended - Easy & Free)

1. **Install Railway CLI**:
   ```bash
   npm i -g @railway/cli
   railway login
   ```

2. **Deploy**:
   ```bash
   railway init
   railway up
   ```

3. **Add Environment Variable**:
   - Go to Railway dashboard
   - Add `GEMINI_API_KEY` in Variables section

Railway automatically detects Flask apps and deploys them.

### Option 2: Render

1. **Connect Repository**:
   - Go to [render.com](https://render.com)
   - New → Web Service
   - Connect your GitHub repo

2. **Configure**:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python web_app.py`
   - **Environment**: Python 3
   - Add `GEMINI_API_KEY` in Environment Variables

3. **Deploy**: Render will automatically deploy

### Option 3: Heroku

1. **Install Heroku CLI**:
   ```bash
   heroku login
   heroku create your-app-name
   ```

2. **Deploy**:
   ```bash
   git push heroku main
   heroku config:set GEMINI_API_KEY=your_key
   ```

3. **Open**:
   ```bash
   heroku open
   ```

### Option 4: PythonAnywhere

1. **Upload Files**:
   - Upload all files via web interface or git

2. **Configure Web App**:
   - Source code: `/home/yourusername/multi-agent-orchestrator`
   - WSGI file: Point to `web_app.py`
   - Add environment variable: `GEMINI_API_KEY`

3. **Reload**: Click reload button

### Option 5: VPS (DigitalOcean, AWS EC2, etc.)

1. **SSH into server**:
   ```bash
   ssh user@your-server-ip
   ```

2. **Clone and setup**:
   ```bash
   git clone https://github.com/Anujpatel04/Multi-agent-orchestrator-system-with-standardized-A2A-Protocol.git
   cd Multi-agent-orchestrator-system-with-standardized-A2A-Protocol
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Setup systemd service** (create `/etc/systemd/system/agent-app.service`):
   ```ini
   [Unit]
   Description=Multi-Agent Orchestrator App
   After=network.target

   [Service]
   User=your-user
   WorkingDirectory=/path/to/Multi-agent-orchestrator-system-with-standardized-A2A-Protocol
   Environment="PATH=/path/to/venv/bin"
   ExecStart=/path/to/venv/bin/python web_app.py
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

4. **Start service**:
   ```bash
   sudo systemctl enable agent-app
   sudo systemctl start agent-app
   ```

## Environment Variables

All platforms need:
- `GEMINI_API_KEY`: Your Google Gemini API key

## Post-Deployment

1. **Test the deployment**: Visit your app URL
2. **Check logs**: Monitor for errors
3. **Update CORS**: If needed, update CORS settings in `web_app.py`

## Notes

- Port configuration: Default is 5001, adjust if needed
- Database: Vector databases are created locally on first run
- Rate limits: Be aware of Gemini API rate limits on free tier

