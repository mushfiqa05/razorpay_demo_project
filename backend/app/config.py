import os
from pydantic import BaseModel

class Settings(BaseModel):
    """
    Centralized configuration for the Razorpay AI Revenue Recovery Control Tower.
    Reads environment variables or uses safe defaults for hackathon development.
    """
    APP_NAME: str = "Razorpay AI Revenue Recovery Control Tower"
    VERSION: str = "1.0.0"
    ENV: str = os.getenv("ENV", "development")
    
    # Database URL: Uses SQLite by default for zero-friction local setup, 
    # but can easily connect to PostgreSQL by changing DB_URL env variable.
    # PostgreSQL example: "postgresql://user:password@localhost:5432/razorpay_recovery"
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "sqlite:///./revenue_recovery.db"
    )

    # Optional AI LLM API Key (OpenAI / Gemini / Anthropic API compatible)
    LLM_API_KEY: str = os.getenv("LLM_API_KEY", "demo-key-ai-explainer")

    # Default Merchant Guardrail Rules (Fallback defaults)
    DEFAULT_MAX_RECOVERY_ATTEMPTS: int = 3
    DEFAULT_MAX_DISCOUNT_PCT: float = 10.0
    DEFAULT_MAX_RECOVERY_WINDOW_DAYS: int = 14

settings = Settings()
