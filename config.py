import os
from dotenv import load_dotenv
load_dotenv()
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./agentic_curriculum.db")
DEBUG = os.getenv("DEBUG", "true").lower() == "true"
GROQ_MODEL = "llama-3.3-70b-versatile"
