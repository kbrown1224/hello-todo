from functools import lru_cache
from pathlib import Path

from pydantic import BaseSettings
import sys


root = Path(__file__).parent.parent
testing = "pytest" in sys.argv[0]


class UISettings(BaseSettings):
    DIST_DIR: Path = root / "frontend" / "dist" / "spa"


class DocumentationSettings(BaseSettings):
    SHOW: bool = True
    VERSION: str = "0.1.0"
    TOS_PATH: str | None = None


class ServerSettings(BaseSettings):
    HOST: str = "127.0.0.1"
    PORT: int = 8000


class CookieSettings(BaseSettings):
    SECRET_KEY: str = "MYSECRET"
    ALGO: str = "HS256"


class DBSettings(BaseSettings):
    URL: str = "sqlite:///test_db.sqlite" if testing else "sqlite:///db.sqlite"


class Settings(BaseSettings):
    docs: DocumentationSettings = DocumentationSettings()
    server: ServerSettings = ServerSettings()
    ui: UISettings = UISettings()
    cookie: CookieSettings = CookieSettings()
    db: DBSettings = DBSettings()


@lru_cache
def get_settings() -> Settings:
    return Settings()
