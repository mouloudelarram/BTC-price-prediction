"""
Configuration management for the Mood Analysis API.
Handles environment variables, validation, and default values.
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List
from pathlib import Path


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # API Configuration
    api_host: str = Field(default="0.0.0.0", alias="API_HOST")
    api_port: int = Field(default=8000, alias="API_PORT")
    api_environment: str = Field(default="development", alias="API_ENVIRONMENT")
    debug: bool = Field(default=False, alias="API_DEBUG")

    # Scrapper Configuration
    scrapper_base_url: str = Field(default="http://localhost:8001", alias="SCRAPPER_BASE_URL")
    scrapper_timeout: int = Field(default=300, alias="SCRAPPER_TIMEOUT")
    scrapper_retries: int = Field(default=3, alias="SCRAPPER_RETRIES")

    # LLM Configuration
    llm_base_url: str = Field(default="http://localhost:8002", alias="LLM_BASE_URL")
    llm_timeout: int = Field(default=120, alias="LLM_TIMEOUT")
    ollama_host: str = Field(default="http://localhost:11434", alias="OLLAMA_HOST")
    ollama_model: str = Field(default="mistral-large-3:675b-cloud", alias="OLLAMA_MODEL")
    concurrency_limit: int = Field(default=3, alias="CONCURRENCY_LIMIT")

    # Data Paths
    data_dir: Path = Field(default=Path("../scrapper/data_sourcing/output"), alias="DATA_DIR")
    checkpoint_dir: Path = Field(default=Path("./checkpoints"), alias="CHECKPOINT_DIR")
    output_dir: Path = Field(default=Path("./output"), alias="OUTPUT_DIR")

    # Logging
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    log_file: Path = Field(default=Path("./logs/api.log"), alias="LOG_FILE")

    # Cache
    cache_enabled: bool = Field(default=True, alias="CACHE_ENABLED")
    cache_ttl: int = Field(default=3600, alias="CACHE_TTL")

    # Security
    api_key_enabled: bool = Field(default=False, alias="API_KEY_ENABLED")
    api_key: str = Field(default="", alias="API_KEY")

    # CORS
    cors_origins: str = Field(default="http://localhost:3000,http://localhost:8000", alias="CORS_ORIGINS")

    # Platform Weights for Mood Analysis
    fear_greed_weight: float = Field(default=0.30, alias="FEAR_GREED_WEIGHT")
    coindesk_weight: float = Field(default=0.25, alias="COINDESK_WEIGHT")
    reddit_weight: float = Field(default=0.15, alias="REDDIT_WEIGHT")
    truth_social_weight: float = Field(default=0.10, alias="TRUTH_SOCIAL_WEIGHT")
    binance_weight: float = Field(default=0.10, alias="BINANCE_WEIGHT")
    coingecko_weight: float = Field(default=0.10, alias="COINGECKO_WEIGHT")

    class Config:
        env_file = ".env"
        case_sensitive = False

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from comma-separated string."""
        return [origin.strip() for origin in self.cors_origins.split(",")]

    @property
    def platform_weights(self) -> dict:
        """Get platform weights as dictionary."""
        return {
            "fear_greed": self.fear_greed_weight,
            "coindesk": self.coindesk_weight,
            "reddit": self.reddit_weight,
            "truth_social": self.truth_social_weight,
            "binance": self.binance_weight,
            "coingecko": self.coingecko_weight,
        }


# Load settings
settings = Settings()

# Ensure required directories exist
settings.checkpoint_dir.mkdir(parents=True, exist_ok=True)
settings.output_dir.mkdir(parents=True, exist_ok=True)
settings.data_dir.parent.mkdir(parents=True, exist_ok=True)
