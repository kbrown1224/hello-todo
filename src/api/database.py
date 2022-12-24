"""Database Connection Pool"""

from databases import Database
from sqlalchemy import MetaData

from api.config import get_settings

settings = get_settings()
metadata = MetaData()
database = Database(url=settings.db.URL)
