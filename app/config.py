from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg://skilledguard:skilledguard@db:5432/skilledguard"

    # Sin valor por defecto a propósito: un secreto quemado en el código es un secreto público.
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    jwt_expiracion_minutos: int = 60


settings = Settings()  # type: ignore[call-arg]
