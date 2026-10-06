from decimal import Decimal

import httpx

from app.rates import CbuRates


# 1-usul: dependency_overrides
def test_price_usd_uses_fake_rates(client, make_car, fake_rates):
    car = make_car(price=Decimal("125000000"))

    response = client.get(f"/api/cars/{car.id}/price-usd")

    assert response.status_code == 200
    assert response.json() == {
        "id": car.id,
        "price_uzs": "125000000.00",
        "rate": "12500",
        "price_usd": "10000.00",
    }


# 2-usul: monkeypatch
def test_cbu_rates_reads_rate(monkeypatch):
    class FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return [{"Ccy": "USD", "Rate": "11778.45"}]

    calls = []

    def fake_get(url, timeout):
        calls.append(url)
        return FakeResponse()

    monkeypatch.setattr(httpx, "get", fake_get)

    assert CbuRates().usd() == Decimal("11778.45")
    assert calls == [CbuRates.url]