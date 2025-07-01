import os


class Config:
    """Configuration values loaded from environment variables."""

    SECRET_KEY = os.getenv("SECRET_KEY", "dev")
