import os


class Settings:
    database_url = os.getenv(
        "DATABASE_URL", "postgresql+psycopg2://postgres:difyai123456@127.0.0.1:5432/test"
    )
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "5000"))
    debug = os.getenv("DEBUG", "false").lower() == "true"
