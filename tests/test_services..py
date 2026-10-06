from decimal import Decimal

import pytest

from app.models import Car
from app.services import CarAlreadySold, price_in_usd, sell


@pytest.mark.parametrize(
    ("price", "rate", "expected"),
    [
        (Decimal("125000000"), Decimal("12500"), Decimal("10000.00")),
        (Decimal("100000"), Decimal("12345.67"), Decimal("8.10")),
        (Decimal("1"), Decimal("3"), Decimal("0.33")),
    ],
)
def test_price_in_usd(price, rate, expected):
    assert price_in_usd(price, rate) == expected


def test_price_in_usd_rejects_zero_rate():
    with pytest.raises(ValueError, match="positive"):
        price_in_usd(Decimal("100"), Decimal("0"))


def test_sell_marks_car_as_sold():
    car = Car(vin="XWB0000000000S001", is_sold=False)
    sell(car)
    assert car.is_sold is True


def test_sell_twice_raises():
    car = Car(vin="XWB0000000000S002", is_sold=True)
    with pytest.raises(CarAlreadySold, match="already sold"):
        sell(car)