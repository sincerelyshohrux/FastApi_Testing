from decimal import ROUND_HALF_UP, Decimal

from app.models import Car


class CarAlreadySold(Exception):
    pass


def price_in_usd(price_uzs: Decimal, rate: Decimal) -> Decimal:
    if rate <= 0:
        raise ValueError("Rate must be positive")
    return (price_uzs / rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def sell(car: Car) -> Car:
    if car.is_sold:
        raise CarAlreadySold(f"Car {car.vin} is already sold")
    car.is_sold = True
    return car