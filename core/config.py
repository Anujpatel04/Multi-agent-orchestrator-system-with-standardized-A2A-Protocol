import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY or GEMINI_API_KEY == "your_gemini_api_key_here":
    raise ValueError(
        "GEMINI_API_KEY not found in environment variables. "
        "Please set it in .env file: GEMINI_API_KEY=your_actual_key"
    )

