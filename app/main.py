# app/main.py
from fastapi import FastAPI
from .schemas import RestaurantSearchRequest, RestaurantSearchResponse
from .service import search_restaurants

app = FastAPI(
    title="POI Restaurant Locator Service",
    description="Microserviço reutilizável para localizar restaurantes (POIs) em uma área geográfica.",
    version="1.0.0",
)

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post(
    "/restaurants/search",
    response_model=RestaurantSearchResponse,
    tags=["restaurants"],
    summary="Busca restaurantes em um raio",
    description="Retorna POIs de restaurantes dentro de uma área geográfica específica."
)
def search_restaurants_endpoint(payload: RestaurantSearchRequest):
    items = search_restaurants(payload)
    return RestaurantSearchResponse(total=len(items), items=items)
