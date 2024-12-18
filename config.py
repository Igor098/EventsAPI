import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    AFISHA_KEY: str
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    )

    def get_db_url(self):
        return (f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@"
                f"{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}")

    def get_sqlite_url(self):
        return f"sqlite+aiosqlite:///data/db.sqlite"


settings = Settings()

print("DB URL =>", settings.get_db_url())
print("DB HOST =>", settings.DB_HOST)
print("DB SQLITE =>", settings.get_sqlite_url())
