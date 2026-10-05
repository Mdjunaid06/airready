"""
Central settings object. Every environment variable the backend reads must be
declared here — never read os.environ directly elsewhere in the app.
See docs/BACKEND.md Section 3 for the convention this follows.
"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    port: int = 8000
    model_path: str = "app/model_artifact/rul_model.pkl"
    cors_origins: str = "http://localhost:5173"

    class Config:
        env_file = ".env"

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


settings = Settings()
