import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen3:1.7b")
TOOLBOX_EXE = os.getenv("TOOLBOX_EXE", r"C:\toolbox\toolbox.exe")
TOOLBOX_CONFIG = os.getenv("TOOLBOX_CONFIG", r"C:\toolbox\tools.yaml")
FASTAPI_BASE_URL = os.getenv("FASTAPI_BASE_URL", "http://127.0.0.1:8000")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not DATABASE_URL:
    raise ValueError("No se encontró DATABASE_URL en el archivo .env")
