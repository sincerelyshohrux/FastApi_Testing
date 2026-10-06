from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.config import settings
from app.db import Base, get_db
from app.main import app
from app.models import Car
from app.rates import get_rates


# Test bazasi: butun sessiyada bitta engine, jadvallar boshida yaratilib oxirida o'chadi.
@pytest.fixture(scope="session")
def engine():
    test_engine = create_engine(settings.test_database_url, echo=settings.sql_echo)
    Base.metadata.drop_all(test_engine)
    Base.metadata.create_all(test_engine)
    yield test_engine
    Base.metadata.drop_all(test_engine)
    test_engine.dispose()


# Har test: tashqi tranzaksiya + SAVEPOINT, oxirida ROLLBACK.
@pytest.fixture
def db_session(engine):
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(
        bind=connection,
        join_transaction_mode="create_savepoint",
        expire_on_commit=False,
    )
    yield session
    session.close()
    transaction.rollback()
    connection.close()


# get_db o'rniga test sessiyasi.
@pytest.fixture
def override_db(db_session):
    def get_test_db():
        yield db_session

    app.dependency_overrides[get_db] = get_test_db
    yield db_session
    app.dependency_overrides.pop(get_db, None)


@pytest.fixture
def client(override_db):
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def api_headers():
    return {"X-API-Key": settings.api_key}


# Bazaga tayyor mashina qo'shadigan fabrika: make_car(brand="BYD").
@pytest.fixture
def make_car(db_session):
    numbers = iter(range(1, 10_000))

    def factory(**fields):
        data = {
            "brand": "Chevrolet",
            "model": "Cobalt",
            "year": 2023,
            "price": Decimal("150000000"),
            "vin": f"XWB0000000000{next(numbers):04d}",
        }
        data.update(fields)
        car = Car(**data)
        db_session.add(car)
        db_session.commit()
        # Bazadagi ko'rinishini qayta o'qiymiz (narx 150000000.00 bo'ladi).
        db_session.refresh(car)
        return car

    return factory


# cbu.uz o'rniga soxta kurs.
class FakeRates:
    def __init__(self, rate: str):
        self.rate = Decimal(rate)

    def usd(self) -> Decimal:
        return self.rate


@pytest.fixture
def fake_rates():
    rates = FakeRates("12500")
    app.dependency_overrides[get_rates] = lambda: rates
    yield rates
    app.dependency_overrides.pop(get_rates, None)


@pytest.fixture
def anyio_backend():
    return "asyncio"