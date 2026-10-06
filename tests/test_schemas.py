from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.schemas import CarCreate

VALID = {
    "brand": "Chevrolet",
    "model": "Cobalt",
    "year": 2023,
    "price": "150000000",
    "vin": "xwb0000000000a001",
}



def test_valid_car_is_normalized():
    car = CarCreate(**VALID)
    assert car.vin == "XWB0000000000A001"
    assert car.price == Decimal("150000000")


@pytest.mark.parametrize(
    ("field", "value", "error_type"),
    [
        ("year", 1949, "greater_than_equal"),
        ("year", 2100, "value_error"),
        ("price", "0", "greater_than"),
        ("vin", "SHORT", "string_too_short"),
        ("brand", "A", "string_too_short"),
    ],
)
def test_invalid_car(field, value, error_type):
    with pytest.raises(ValidationError) as info:
        CarCreate(**{**VALID, field: value})
    error = info.value.errors()[0]
    assert error["loc"] == (field,)
    assert error["type"] == error_type