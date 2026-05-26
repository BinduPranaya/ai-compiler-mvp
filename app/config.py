import os
from dotenv import load_dotenv

# Load standard .env file if it exists
load_dotenv()

class Settings:
    def __init__(self):
        self.PORT = int(os.getenv("PORT", 8000))
        self.HOST = os.getenv("HOST", "127.0.0.1")
        self.DEBUG = os.getenv("DEBUG", "True").lower() in ("true", "1", "yes")
        self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
        self.GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
        self.OUTPUT_PATH = os.getenv("OUTPUT_PATH", "outputs/generated.json")

# Instantiate settings
settings = Settings()
