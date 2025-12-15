# Serviço POI para Localização de Restaurantes

Microserviço **SOA reutilizável** para localização geográfica de restaurantes (POIs) dentro de uma área especificada.
O serviço utiliza **dados reais do OpenStreetMap (OSM)** por meio da **Overpass API** e aplica **padrões arquiteturais de resiliência** para garantir estabilidade e reuso em ambientes distribuídos.

Documento PDF do Relatório: [Relatório Reuso - Trabalho 2.pdf](https://github.com/user-attachments/files/24177185/Relatorio.Reuso.-.Trabalho.2.pdf)


---

## 1. Objetivo do Projeto

Este serviço foi projetado para atender aos requisitos do trabalho prático de **Reuso de Software**, demonstrando:

* Construção de um **serviço reutilizável**
* Aplicação prática de conceitos de **SOA/Microserviços**
* Uso explícito de **padrões arquiteturais de resiliência**
* Separação clara de responsabilidades e baixo acoplamento

---

## 2. Funcionalidades

* Busca restaurantes em um **raio definido (km)** a partir de coordenadas geográficas
* Integração com **fonte de dados real** (OpenStreetMap / Overpass API)
* API **REST** documentada automaticamente pelo FastAPI
* Implementação de **Retry com Exponential Backoff**
* Implementação de **Circuit Breaker** para proteção contra falhas repetidas
* Cache em memória com **TTL** para reduzir chamadas externas
* Cálculo de distância geográfica real usando a **fórmula de Haversine**
* Serviço **simples, modular e reutilizável** para qualquer arquitetura SOA/Microserviços

---

## 3. Arquitetura

O serviço segue uma arquitetura **SOA**, com separação clara de responsabilidades:

```
app/
├── cache.py        # Cache em memória com TTL
├── main.py         # Camada de API (FastAPI)
├── service.py      # Lógica de negócio e integração com OSM
├── models.py       # Modelos de domínio
├── schemas.py      # Schemas de entrada e saída (Pydantic)
├── utils.py        # Funções utilitárias (Haversine)
└── resilience.py   # Retry + Exponential Backoff + Circuit Breaker
```

Essa organização facilita:

* Reuso do serviço
* Evolução independente
* Testabilidade
* Manutenção

---

## 4. Resiliência e Tolerância a Falhas

### Retry com Exponential Backoff

* 3 tentativas automáticas
* Delay inicial: **0.5s**
* Backoff exponencial (delay dobra a cada falha)
* Tratamento transparente de falhas temporárias da Overpass API

Exemplo de log:

```
Tentativa 1 falhou: HTTP 429. Nova tentativa em 0.50s.
Tentativa 2 falhou: Timeout. Nova tentativa em 1.00s.
```

### Circuit Breaker

* Limite de falhas consecutivas configurável
* Bloqueia chamadas quando o serviço externo está instável
* Retorno controlado com erro HTTP 503

---

## 5. Requisitos

### Dependências

O arquivo `requirements.txt` **fica na raiz do projeto (fora da pasta app)**:

```
fastapi
uvicorn
pydantic
httpx
```

Instalação:

```bash
pip install -r requirements.txt
```

---

## 6. Como Executar

### 1. Clone ou copie o projeto

```bash
git clone <seu-repositorio>
cd <seu-repositorio>
```

### 2. Instale as dependências

```bash
pip install -r requirements.txt
```

### 3. Suba o servidor

```bash
uvicorn app.main:app --reload
```

### 4. Acesse a documentação automática

* **Swagger UI:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
* **ReDoc:** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## 7. Endpoints

### Health Check

**GET** `/health`

Resposta:

```json
{ "status": "ok" }
```

### Buscar Restaurantes

**POST** `/restaurants/search`

Corpo da requisição:

```json
{
  "center": { "lat": -23.5505, "lon": -46.6333 },
  "radius_km": 2
}
```

Resposta:

```json
{
  "total": 3,
  "items": [
    {
      "id": 123456,
      "name": "Restaurante Exemplo",
      "category": "restaurant",
      "location": {
        "lat": -23.5512,
        "lon": -46.6318
      }
    }
  ]
}
```

---

## 8. Exemplos de Coordenadas para Teste

### Fortaleza – CE (Centro)

```json
{
  "center": {
    "lat": -3.7327,
    "lon": -38.5270
  },
  "radius_km": 5
}
```

### Quixadá – CE (Centro)

```json
{
  "center": {
    "lat": -4.9721,
    "lon": -39.0150
  },
  "radius_km": 3
}
```

### Quixadá – CE (Bairro Campo Novo)

```json
{
  "center": {
    "lat": -4.9659,
    "lon": -39.0196
  },
  "radius_km": 2
}
```

---
