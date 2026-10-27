"""
Settings are read from environment variables so the same code can
run locally (with defaults) and on a hosting platform like Render
(where these get set in the dashboard instead).
"""

import os


class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///mealmuse.db")
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-not-secure")
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")  # read directly by ai_service.py
