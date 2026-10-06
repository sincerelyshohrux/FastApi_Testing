from decimal import Decimal

import httpx


class CbuRates:
    url = "https://cbu.uz/uz/arkhiv-kursov-valyut/json/USD/"

    def usd(self) -> Decimal:
        response = httpx.get(self.url, timeout=5)
        response.raise_for_status()
        # Javob: [{"Ccy": "USD", "Rate": "11778.45", ...}]
        return Decimal(response.json()[0]["Rate"])


def get_rates() -> CbuRates:
    return CbuRates()