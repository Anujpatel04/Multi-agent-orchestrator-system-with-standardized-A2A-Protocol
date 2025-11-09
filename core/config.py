import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Primary API key (used by Agent 1)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_API_KEY_AGENT1 = os.getenv("GEMINI_API_KEY_AGENT1", GEMINI_API_KEY)

# Orchestrator uses DeepSeek API
DEEPSEEK_API_KEY_ORCHESTRATOR = os.getenv("DEEPSEEK_API_KEY_ORCHESTRATOR")
GEMINI_API_KEY_ORCHESTRATOR = os.getenv("GEMINI_API_KEY_ORCHESTRATOR", GEMINI_API_KEY)  # Fallback if DeepSeek not available

# Agent 2 uses DeepSeek API
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
GEMINI_API_KEY_AGENT2 = os.getenv("GEMINI_API_KEY_AGENT2")  # Fallback if DeepSeek not available

# Validate at least one key is set
if not GEMINI_API_KEY or GEMINI_API_KEY == "your_gemini_api_key_here":
    if not DEEPSEEK_API_KEY or DEEPSEEK_API_KEY == "your_deepseek_api_key_here":
        if not GEMINI_API_KEY_AGENT2 or GEMINI_API_KEY_AGENT2 == "your_gemini_api_key_here":
            raise ValueError(
                "GEMINI_API_KEY or DEEPSEEK_API_KEY not found in environment variables. "
                "Please set at least GEMINI_API_KEY in .env file: GEMINI_API_KEY=your_actual_key"
            )

