import pytest
from httpx2 import ASGITransport, AsyncClient

from app.main import app


@pytest.mark.anyio
async def test_list_cars_async(override_db, make_car):
    make_car(model="Gentra")

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/cars")

    assert response.status_code == 200
    assert [car["model"] for car in response.json()] == ["Gentra"]