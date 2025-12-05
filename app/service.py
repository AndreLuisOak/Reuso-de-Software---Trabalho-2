# app/service.py
import httpx
from typing import List
from .models import RestaurantPOI, Location
from .schemas import RestaurantSearchRequest, RestaurantItem
from .resilience import retry, RetryConfig
from .utils import haversine_km
import logging

logger = logging.getLogger("poi-service")

OVERPASS_URL = "https://overpass-api.de/api/interpreter"


@retry(RetryConfig(retries=3, delay_seconds=0.5, backoff_factor=2.0))
def _query_overpass(query: str) -> dict:
    response = httpx.post(OVERPASS_URL, data={"data": query}, timeout=20)
    response.raise_for_status()
    return response.json()


def search_restaurants(req: RestaurantSearchRequest) -> List[RestaurantItem]:
    """
    Busca real de POIs no OpenStreetMap via Overpass API.
    """

    lat = req.center.lat
    lon = req.center.lon
    radius_m = int(req.radius_km * 1000)

    overpass_query = f"""
        [out:json];
        node
          ["amenity"="restaurant"]
          (around:{radius_m},{lat},{lon});
        out center;
    """

    raw_data = _query_overpass(overpass_query)

    results = []

    for e in raw_data.get("elements", []):
        name = e.get("tags", {}).get("name")
        if not name:
            continue  # ignora restaurantes sem nome

        location = Location(lat=e["lat"], lon=e["lon"])

        poi = RestaurantPOI(
            id=str(e["id"]),
            name=name,
            location=location
        )

        # filtro final pelo haversine (garantia)
        if haversine_km(req.center, location) <= req.radius_km:
            results.append(RestaurantItem(**poi.dict()))

    return results
