# Serviço POI para Localização de Restaurantes

Microserviço **SOA reutilizável** para localização geográfica de restaurantes (POIs) dentro de uma área especificada.  
O serviço utiliza **dados reais do OpenStreetMap (OSM)** por meio da **Overpass API** e aplica **padrões arquiteturais de resiliência** para garantir estabilidade e reuso em ambientes distribuídos.

---

## 1. Objetivo do Projeto

Este serviço foi projetado para atender aos requisitos do trabalho prático de **Reuso de Software**, demonstrando:

- Construção de um **serviço reutilizável**
- Aplicação prática de conceitos de **SOA/Microserviços**
- Uso explícito de **padrões arquiteturais de resiliência**
- Separação clara de responsabilidades e baixo acoplamento

---

## 2. Funcionalidades

- Busca restaurantes em um **raio definido (km)** a partir de coordenadas geográficas
- Integração com **fonte de dados real** (OpenStreetMap / Overpass API)
- API **REST** documentada automaticamente pelo FastAPI
- Implementação de **Retry com Exponential Backoff**
- Cálculo de distância geográfica real usando a **fórmula de Haversine**
- Serviço **simples, modular e reutilizável** para qualquer arquitetura SOA/Microserviços

---

## 3. Arquitetura

O serviço segue uma arquitetura **SOA**, com separação clara de responsabilidades:

app/
├── cache.py
├── main.py
├── service.py
├── models.py
├── schemas.py
├── utils.py
└── resilience.py

Essa organização facilita:
- Reuso do serviço
- Evolução independente
- Testabilidade
- Manutenção

---
- 3 tentativas automáticas
- Delay inicial: **0.5s**
- Backoff exponencial (delay dobra a cada falha)
- Tratamento transparente de falhas temporárias da Overpass API

Exemplo de log:
Tentativa 1 falhou: HTTP 429. Nova tentativa em 0.50s.
Tentativa 2 falhou: Timeout. Nova tentativa em 1.00s.

---

Inclua no arquivo `requirements.txt`:

fastapi
uvicorn
pydantic
httpx

Instalação:
pip install -r requirements.txt

Como Executar

Clone ou copie o projeto

Copiar código
git clone <seu-repositorio>
cd <seu-repositorio>

Instale as dependências

Copiar código
pip install -r requirements.txt

Suba o servidor

Copiar código
uvicorn app.main:app --reload

Acesse a documentação automática
Swagger UI
http://127.0.0.1:8000/docs

ReDoc
http://127.0.0.1:8000/redoc

Endpoints
Health Check
GET /health

Resposta:

json
Copiar código
{ "status": "ok" }
Buscar Restaurantes
POST /restaurants/search

Corpo da requisição
json
Copiar código
{
  "center": { "lat": -23.5505, "lon": -46.6333 },
  "radius_km": 2
}

Resposta
json
Copiar código
{
  "total": 3,
  "items": [
    {
      "id": "123456",
      "name": "Restaurante Exemplo",
      "category": "restaurant",
      "location": {
        "lat": -23.5512,
        "lon": -46.6318
      }
    }
  ]
}

Exemplos de Coordenadas para Teste
Fortaleza – CE (Centro)
json
Copiar código
{
  "center": {
    "lat": -3.7327,
    "lon": -38.5270
  },
  "radius_km": 5
}
Quixadá – CE (Centro)
json
Copiar código
{
  "center": {
    "lat": -4.9721,
    "lon": -39.0150
  },
  "radius_km": 3
}
Quixadá – CE (Bairro Campo Novo)
json
Copiar código
{
  "center": {
    "lat": -4.9659,
    "lon": -39.0196
  },
  "radius_km": 2
}