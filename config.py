import os
from dotenv import load_dotenv

# Load variables from the .env file into the environment
load_dotenv()

class Config:
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_NAME = os.getenv("DB_NAME", "finance_tracker")
    SECRET_KEY = os.getenv("SECRET_KEY", "dev_secret_key")