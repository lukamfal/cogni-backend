from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    APP_NAME: str = "CogniMente"
    APP_ENV: str = "development"
    SECRET_KEY: str = "change-me-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080  # 7 dias

    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/cognimente"
    REDIS_URL: str = "redis://localhost:6379/0"

    S3_BUCKET_NAME: str = "cognimente-media"
    S3_REGION: str = "us-east-1"
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    S3_ENDPOINT_URL: str = ""

    ALLOWED_ORIGINS: str = "http://localhost:3000"
    # Endereço público da API, usado nos links das fotos enviadas.
    PUBLIC_BASE_URL: str = "http://localhost:8000"

    @property
    def origins_list(self) -> List[str]:
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",")]

    @property
    def is_development(self) -> bool:
        return self.APP_ENV.lower() in ("development", "dev", "local")

    class Config:
        env_file = ".env"


# Chaves de exemplo que nunca podem ir para produção: com elas, qualquer um cria logins falsos.
_PLACEHOLDER_KEYS = {"change-me-in-production", "your-super-secret-key-change-in-production", ""}

settings = Settings()

_weak_key = (
    settings.SECRET_KEY in _PLACEHOLDER_KEYS
    or settings.SECRET_KEY.startswith("gere-com")  # texto de exemplo do .env.example
    or len(settings.SECRET_KEY) < 32
)
if not settings.is_development and _weak_key:
    raise RuntimeError(
        "SECRET_KEY inseguro. Defina no .env uma chave aleatória com 32+ caracteres "
        "(por exemplo: python -c \"import secrets; print(secrets.token_hex(32))\")."
    )
