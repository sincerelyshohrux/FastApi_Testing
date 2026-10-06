from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import settings

engine = create_engine(settings.database_url, echo=settings.sql_echo)
SessionLocal = sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


# Testlarda aynan shu funksiya test sessiyasi bilan almashtiriladi.
def get_db() -> Iterator[Session]:
    with SessionLocal() as session:
        yield session