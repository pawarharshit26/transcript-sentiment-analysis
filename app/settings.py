import os
from dotenv import load_dotenv

# load .env once for whole project
load_dotenv()


DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://postgres:postgres@db:5432/postgres"
)
REDIS_URL = os.getenv(
    "REDIS_URL", "redis://redis:6379/0"
)