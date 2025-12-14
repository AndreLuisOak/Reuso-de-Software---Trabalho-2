from typing import List
from pydantic import BaseModel
from .models import Location, SearchArea

class RestaurantItem(BaseModel):
    id: int
    name: str
    category: str
    location: Location

class RestaurantSearchRequest(SearchArea):
    pass

class RestaurantSearchResponse(BaseModel):
    total: int
    items: List[RestaurantItem]
