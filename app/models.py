from datetime import datetime
from decimal import Decimal

from sqlalchemy import CheckConstraint, DateTime, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class Car(Base):
    __tablename__ = "cars"
    __table_args__ = (
        CheckConstraint("year >= 1950", name="year_min"),
        CheckConstraint("price > 0", name="price_positive"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    brand: Mapped[str] = mapped_column(String(50), index=True)
    model: Mapped[str] = mapped_column(String(50))
    year: Mapped[int]
    price: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    vin: Mapped[str] = mapped_column(String(17), unique=True)
    is_sold: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )