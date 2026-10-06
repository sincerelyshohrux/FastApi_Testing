from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.deps import CarDep, DbSession, RatesDep, require_api_key
from app.models import Car
from app.schemas import CarCreate, CarPriceUsd, CarRead, CarUpdate
from app.services import CarAlreadySold, price_in_usd, sell

router = APIRouter(prefix="/api/cars", tags=["cars"])

WRITE = [Depends(require_api_key)]


@router.post("", response_model=CarRead, status_code=201, dependencies=WRITE)
def create_car(data: CarCreate, db: DbSession):
    car = Car(**data.model_dump())
    db.add(car)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status.HTTP_409_CONFLICT, "Car with this VIN already exists"
        ) from None
    db.refresh(car)
    return car


@router.get("", response_model=list[CarRead])
def list_cars(
    db: DbSession,
    brand: str | None = None,
    is_sold: bool | None = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
):
    stmt = select(Car).order_by(Car.id)
    if brand:
        stmt = stmt.where(Car.brand.ilike(brand))
    if is_sold is not None:
        stmt = stmt.where(Car.is_sold == is_sold)
    return db.scalars(stmt.limit(limit).offset(offset)).all()


@router.get("/{car_id}", response_model=CarRead)
def get_car(car: CarDep):
    return car


@router.patch("/{car_id}", response_model=CarRead, dependencies=WRITE)
def update_car(data: CarUpdate, car: CarDep, db: DbSession):
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(car, field, value)
    db.commit()
    db.refresh(car)
    return car


@router.delete("/{car_id}", status_code=204, dependencies=WRITE)
def delete_car(car: CarDep, db: DbSession):
    db.delete(car)
    db.commit()


@router.post("/{car_id}/sell", response_model=CarRead, dependencies=WRITE)
def sell_car(car: CarDep, db: DbSession):
    try:
        sell(car)
    except CarAlreadySold as error:
        raise HTTPException(status.HTTP_409_CONFLICT, str(error)) from None
    db.commit()
    return car


@router.get("/{car_id}/price-usd", response_model=CarPriceUsd)
def car_price_usd(car: CarDep, rates: RatesDep):
    rate = rates.usd()
    return CarPriceUsd(
        id=car.id,
        price_uzs=car.price,
        rate=rate,
        price_usd=price_in_usd(car.price, rate),
    )