from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    GEMINI_API_KEY: str = ""
    CHROMA_PERSIST_DIR: str = str(Path(__file__).parent.parent.parent / "data" / "chroma")
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    TOP_K_RESULTS: int = 5

    class Config:
        env_file = ".env"


settings = Settings()
