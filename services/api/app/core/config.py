"""Configuração central da aplicação usando pydantic-settings."""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    app_name: str = "UNIR Platform API"
    version: str = "0.1.0"
    debug: bool = False

    # Base de dados
    database_url: str = "sqlite:///./unir.db"

    # JWT
    secret_key: str = "super-secret-key-muda-isto-em-producao"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7  # 7 dias

    # CORS
    allowed_origins: list[str] = [
        "http://localhost:3000",
        "http://localhost:8080",
        "https://rafatocantins.github.io",
        "https://unir.pt",
    ]

    # Google Sheets (assinaturas existentes)
    sheet_id: Optional[str] = None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
