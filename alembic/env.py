from app import config
from app.config import settings
from app.models import Base

config.set_main_option("sqlalchemy.url", settings.database_url)
target_metadata = Base.metadata

