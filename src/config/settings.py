import os

from dotenv import load_dotenv
load_dotenv()

class Settings:
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL_NAME: str = "gpt-5-mini"

    GOOGLE_CREDENTIALS_PATH = os.getenv("GOOGLE_CREDENTIALS_PATH")
    GOOGLE_TOKEN_PATH = os.getenv("GOOGLE_TOKEN_PATH")

settings = Settings()