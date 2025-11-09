# Setup Instructions

## Prerequisites

- Python 3.9 or higher
- Google Gemini API key

## Installation Steps

1. **Clone the repository**

   ```bash
   git clone https://github.com/yourusername/multi-agent-orchestrator.git
   cd multi-agent-orchestrator
   ```
2. **Create virtual environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```
4. **Configure environment**

   Create a `.env` file with your API keys:
   
   ```bash
   # Minimum setup (single key - slower):
   GEMINI_API_KEY=your_gemini_api_key_here
   
   # Recommended setup (multiple APIs - fastest parallel processing):
   GEMINI_API_KEY=your_gemini_api_key_here
   GEMINI_API_KEY_AGENT1=your_gemini_api_key_here      # Gemini for Agent 1
   DEEPSEEK_API_KEY_ORCHESTRATOR=your_deepseek_key   # DeepSeek for Orchestrator
   DEEPSEEK_API_KEY=your_deepseek_api_key_here       # DeepSeek API for Agent 2
   ```
   
   **Note:** 
   - Orchestrator uses DeepSeek API for routing and aggregation
   - Agent 1 uses Gemini API
   - Agent 2 uses DeepSeek API (different from Agent 1) for better parallel processing
   - If DeepSeek keys are not provided, components will fallback to Gemini
   - Using different APIs allows all components to process queries in parallel, making the system much faster!
5. **Run the application**

   ```bash
   python web_app.py
   ```
6. **Access the dashboard**
   Open your browser and navigate to: `http://localhost:5001`

## First Run

After starting the application, you can:

1. Use the chat interface to interact with agents
2. Populate sample schedules: `python scripts/populate_routines.py`
3. Query agents separately: `python scripts/query_agents.py`

## Troubleshooting

### API Key Issues

- Ensure `.env` file exists and contains `GEMINI_API_KEY=your_key`
- Check that your API key is valid and has quota remaining

### Port Already in Use

- Change port in `web_app.py`: `app.run(port=5002)`

### Rate Limit Errors

- Free tier allows 2 requests per minute
- Scripts include delays to handle rate limits automatically
