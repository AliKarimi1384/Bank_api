from pydantic_settings import BaseSettings

class Settings(BaseSettings):

    PROJECT_NAME: str = "Bank API"
    DATABASE_URL: str

    #task limits
    DAILY_TRANSACTION_LIMIT: int = 50_000_000
    MIN_TRANSACTION_AMOUNT: int = 1_000
    MAX_TRANSACTION_AMOUNT: int = 50_000_000
    TRANSACTION_FEE_PERCENTAGE: float = 0.10
    MAX_TRANSACTION_FEE: int = 100_000
    API_KEY: str

    class Config:
        env_file = ".env"

settings = Settings()