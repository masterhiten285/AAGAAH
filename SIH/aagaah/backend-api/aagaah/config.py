from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT = Path(__file__).resolve().parents[2]

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='AAGAAH_', env_file='.env', extra='ignore')
    database_url: str | None = None
    redis_url: str | None = None
    demo_memory: bool = False
    schedule: bool = False
    interval_seconds: int = 8
    control_token: str = 'local-demo-only'
    cors_origins: list[str] = ['http://localhost:5173', 'http://127.0.0.1:5173', 'http://localhost:8080']

