# app/models.py
from pydantic import BaseModel, Field


class Location(BaseModel):
    lat: float = Field(..., description="Latitude em graus decimais")
    lon: float = Field(..., description="Longitude em graus decimais")


class RestaurantPOI(BaseModel):
    id: str
    name: str
    category: str = "restaurant"
    location: Location


class SearchArea(BaseModel):
    center: Location
    radius_km: float = Field(..., gt=0, description="Raio da busca em km")
