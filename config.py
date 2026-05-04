import os
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./agentic_curriculum.db")
DEBUG = os.getenv("DEBUG", "true").lower() == "true"
MODEL = "claude-sonnet-4-20250514"
MAX_TOKENS = 1000
