import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    POSTGRES_CONNECTION_STRING = str(os.getenv("POSTGRES_CONNECTION_STRING"))
    PROVIDER_BASE_URL = str(os.getenv("PROVIDER_BASE_URL"))
    PROVIDER_API_KEY = str(os.getenv("API_KEY"))

settings = Settings()