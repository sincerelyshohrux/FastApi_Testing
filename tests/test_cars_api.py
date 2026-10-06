import pytest
from sqlalchemy import func, select

from app.models import Car

NEW_CAR = {
    "brand": "Chevrolet",
    "model": "Malibu",
    "year": 2024,
    "price": "320000000",
    "vin": "XWB0000000000M001",
}


def test_database_is_empty_at_start(db_session):
    count = db_session.scalar(select(func.count()).select_from(Car))
    assert count == 0


def test_create_car(client, api_headers, db_session):
    response = client.post("/api/cars", json=NEW_CAR, headers=api_headers)

    assert response.status_code == 201
    body = response.json()
    assert body["id"] > 0
    assert body["vin"] == NEW_CAR["vin"]
    assert body["price"] == "320000000.00"
    assert body["is_sold"] is False

    car = db_session.get(Car, body["id"])
    assert car.model == "Malibu"


def test_create_car_requires_api_key(client):
    response = client.post("/api/cars", json=NEW_CAR)
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid or missing API key"}


def test_create_car_wrong_api_key(client):
    response = client.post(
        "/api/cars", json=NEW_CAR, headers={"X-API-Key": "wrong-key"}
    )
    assert response.status_code == 401


def test_create_duplicate_vin(client, api_headers, make_car):
    make_car(vin=NEW_CAR["vin"])
    response = client.post("/api/cars", json=NEW_CAR, headers=api_headers)
    assert response.status_code == 409
    assert response.json() == {"detail": "Car with this VIN already exists"}


@pytest.mark.parametrize(
    ("field", "value"),
    [("year", 1900), ("price", "-5"), ("vin", "123")],
)
def test_create_car_validation(client, api_headers, field, value):
    response = client.post(
        "/api/cars", json={**NEW_CAR, field: value}, headers=api_headers
    )
    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", field]


def test_list_cars(client, make_car):
    make_car(brand="Chevrolet", model="Cobalt")
    make_car(brand="BYD", model="Song Plus")
    make_car(brand="Chevrolet", model="Tracker")

    response = client.get("/api/cars")

    assert response.status_code == 200
    assert [car["model"] for car in response.json()] == [
        "Cobalt",
        "Song Plus",
        "Tracker",
    ]


def test_filter_by_brand_ignores_case(client, make_car):
    make_car(brand="Chevrolet")
    make_car(brand="BYD", model="Song Plus")

    response = client.get("/api/cars", params={"brand": "byd"})

    assert [car["brand"] for car in response.json()] == ["BYD"]


# id'lar testdan testga oshib boradi, shuning uchun yaratilgan obyektlarning id'si solishtiriladi.
def test_pagination(client, make_car):
    cars = [make_car() for _ in range(5)]

    response = client.get("/api/cars", params={"limit": 2, "offset": 2})

    assert [car["id"] for car in response.json()] == [cars[2].id, cars[3].id]


def test_get_car(client, make_car):
    car = make_car()
    response = client.get(f"/api/cars/{car.id}")
    assert response.status_code == 200
    assert response.json()["vin"] == car.vin


def test_get_car_not_found(client):
    response = client.get("/api/cars/999999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Car not found"}


def test_update_price(client, api_headers, make_car):
    car = make_car()
    response = client.patch(
        f"/api/cars/{car.id}", json={"price": "140000000"}, headers=api_headers
    )
    assert response.status_code == 200
    assert response.json()["price"] == "140000000.00"
    assert response.json()["model"] == car.model


def test_delete_car(client, api_headers, make_car, db_session):
    car = make_car()
    car_id = car.id
    response = client.delete(f"/api/cars/{car_id}", headers=api_headers)
    assert response.status_code == 204
    assert client.get(f"/api/cars/{car_id}").status_code == 404
    assert db_session.get(Car, car_id) is None


def test_sell_car_twice(client, api_headers, make_car):
    car = make_car()
    first = client.post(f"/api/cars/{car.id}/sell", headers=api_headers)
    second = client.post(f"/api/cars/{car.id}/sell", headers=api_headers)

    assert first.status_code == 200
    assert first.json()["is_sold"] is True
    assert second.status_code == 409
    assert "already sold" in second.json()["detail"]