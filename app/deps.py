from typing import Annotated

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.config import settings
from app.db import get_db
from app.models import Car
from app.rates import CbuRates, get_rates

DbSession = Annotated[Session, Depends(get_db)]


def require_api_key(
    x_api_key: Annotated[str | None, Header()] = None,
) -> None:
    if x_api_key != settings.api_key:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED, "Invalid or missing API key"
        )


def get_car_or_404(car_id: int, db: DbSession) -> Car:
    car = db.get(Car, car_id)
    if car is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Car not found")
    return car


CarDep = Annotated[Car, Depends(get_car_or_404)]
RatesDep = Annotated[CbuRates, Depends(get_rates)]