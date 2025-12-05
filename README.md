Serviço POI Para Localização de Restaurantes

Microserviço SOA reutilizável para localização geográfica de restaurantes (POIs) dentro de uma área especificada.
O serviço utiliza dados reais do OpenStreetMap via Overpass API e aplica um padrão arquitetural de resiliência (Retry com backoff exponencial) para garantir estabilidade em chamadas externas.

1. Funcionalidades

Busca restaurantes em um raio definido (em km) a partir de uma coordenada geográfica.

Fonte de dados real via Overpass API.

API REST documentada automaticamente pelo FastAPI.

Implementação do padrão de resiliência Retry + Exponential Backoff.

Distância geográfica real calculada com a fórmula de Haversine.

Serviço simples, modular e reutilizável para qualquer sistema SOA/Microserviço.

2. Arquitetura

O serviço segue uma arquitetura SOA com separação clara de responsabilidades:

app/
 ├── main.py           # API FastAPI
 ├── service.py        # Lógica de negócio e integração OSM
 ├── models.py         # Modelos internos (POI, Location)
 ├── schemas.py        # Schemas para entrada e saída (Pydantic)
 ├── utils.py          # Funções auxiliares (Haversine)
 └── resilience.py     # Retry + Exponential Backoff

3. Requisitos
Dependências Python

Inclua no seu requirements.txt:

fastapi
uvicorn
pydantic
httpx


Instale com:

pip install -r requirements.txt

4. Como Executar
1. Clone ou copie o projeto
git clone <seu-repo>
cd seu-repo

2. Instale as dependências
pip install -r requirements.txt

3. Suba o servidor
uvicorn app.main:app --reload

4. Acesse a documentação automática

Swagger UI:

http://127.0.0.1:8000/docs


ReDoc:

http://127.0.0.1:8000/redoc

5. Endpoints
Health Check
GET /health


Retorno:

{"status": "ok"}

Buscar Restaurantes
POST /restaurants/search

Corpo da requisição
{
  "center": { "lat": -23.5505, "lon": -46.6333 },
  "radius_km": 2
}

Resposta
{
  "total": 3,
  "items": [
    {
      "id": "123456",
      "name": "Restaurante Exemplo",
      "category": "restaurant",
      "location": { "lat": -23.5512, "lon": -46.6318 }
    }
  ]
}

6. Como Funciona a Busca

Recebe um ponto geográfico + raio em km.

Envia um query Overpass para buscar restaurantes reais.

Filtra novamente pela fórmula de Haversine para garantir precisão.

Retorna lista de restaurantes com ID, nome e coordenadas.

7. Resiliência: Retry com Exponential Backoff

Chamadas à Overpass API são encapsuladas em um decorator:

3 tentativas

Delay inicial: 0.5s

Delay dobra a cada falha

Tratamento automático de exceções

Exemplo de log:

Tentativa 1 falhou: HTTP 429. Nova tentativa em 0.50s.
Tentativa 2 falhou: Timeout. Nova tentativa em 1.00s.