"""Configuration management."""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Application configuration."""

    OPENAI_API_KEY: str = os.getenv("OPEN_AI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o")

    # Paths
    BASE_DIR: Path = Path(__file__).parent.parent
    DATA_DIR: Path = BASE_DIR / "data"
    OUTPUT_DIR: Path = BASE_DIR / "output"

    # Execution limits
    MAX_EXECUTION_TIME: int = 30  # seconds
    MAX_OUTPUT_ROWS: int = 100  # for display

    # Chat history
    HISTORY_LENGTH: int = 50  # last N message pairs to include

    @classmethod
    def validate(cls) -> None:
        """Validate required configuration."""
        if not cls.OPENAI_API_KEY:
            raise ValueError("OPEN_AI_API_KEY is required. Set it in .env file.")
        cls.DATA_DIR.mkdir(parents=True, exist_ok=True)
        cls.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
