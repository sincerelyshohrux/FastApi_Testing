from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class CarCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    brand: str = Field(min_length=2, max_length=50)
    model: str = Field(min_length=1, max_length=50)
    year: int = Field(ge=1950)
    price: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    vin: str = Field(min_length=17, max_length=17)

    @field_validator("year")
    @classmethod
    def not_in_future(cls, value: int) -> int:
        if value > date.today().year + 1:
            raise ValueError("Year cannot be in the future")
        return value

    @field_validator("vin")
    @classmethod
    def upper_vin(cls, value: str) -> str:
        return value.upper()


class CarUpdate(BaseModel):
    brand: str | None = Field(None, min_length=2, max_length=50)
    model: str | None = Field(None, min_length=1, max_length=50)
    price: Decimal | None = Field(None, gt=0, max_digits=12, decimal_places=2)


class CarRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    brand: str
    model: str
    year: int
    price: Decimal
    vin: str
    is_sold: bool


class CarPriceUsd(BaseModel):
    id: int
    price_uzs: Decimal
    rate: Decimal
    price_usd: Decimal