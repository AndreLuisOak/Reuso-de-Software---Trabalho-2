Como executar (local)

crie um virtualenv e instale: pip install -r requirements.txt

exporte variáveis (ex.: export JWT_SECRET="uma_chave_secreta_forte").

rode: uvicorn main:app --reload --port 8000

abra http://localhost:8000/docs para testar via Swagger UI.
