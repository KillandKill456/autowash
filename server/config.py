import os

DB_URL = os.getenv("DB_URL", "postgresql+psycopg2://postgres:123456789@localhost:5432/wash_db")
JWT_SECRET = os.getenv("JWT_SECRET", "change-me")
JWT_ALG = "HS256"
JWT_TTL_MIN = 60 * 24