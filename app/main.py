from fastapi import FastAPI
from .schemas import RestaurantSearchRequest, RestaurantSearchResponse
from .service import search_restaurants

app = FastAPI(
    title="Serviço de POI - Restaurantes",
    description="Microserviço reutilizável para localizar restaurantes (POIs)",
    version="1.0.0",
)

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post(
    "/restaurants/search",
    response_model=RestaurantSearchResponse,
    tags=["restaurants"],
    summary="Busca restaurantes em um raio Km",
    description="Retorna POIs de restaurantes de uma área específica."
)
def search_restaurants_endpoint(payload: RestaurantSearchRequest):
    items = search_restaurants(payload)
    return RestaurantSearchResponse(total=len(items), items=items)
