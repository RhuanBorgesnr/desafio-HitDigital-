# Consulta de usuários

Aplicação Full Stack que recebe uma lista de IDs, consulta cada usuário em uma
API HTTP externa **de forma assíncrona** e devolve, separadamente, os usuários
obtidos e os IDs que falharam. A falha de um usuário **não** interrompe os demais.

- **Backend:** Python + FastAPI (async, `httpx`, validação com Pydantic).
- **Frontend:** React + TypeScript (Vite).
- **Provider externo:** [jsonplaceholder](https://jsonplaceholder.typicode.com)
  (IDs 1–10 existem; 11+ retornam 404 — ótimo para ver `users` e `failed`).

```
POST /api/users/fetch
{ "user_ids": [1, 2, 3, 11] }
->
{ "users": [{ "id": 1, "name": "Leanne Graham" }, ...], "failed": [11] }
```

## Como executar

### Backend (porta 8000)

```bash
cd backend
python -m venv .venv
# Windows:  .venv\Scripts\activate
# Linux/Mac: source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Docs interativas em `http://localhost:8000/docs`.

### Frontend (porta 5173)

```bash
cd frontend
npm install
npm run dev
```

Abra `http://localhost:5173`. Se o backend não estiver em `localhost:8000`,
defina `VITE_API_URL`.

### Testes

```bash
cd backend
pytest
```

## Principais decisões técnicas

- **FastAPI + async:** o problema é I/O-bound (várias chamadas HTTP). `async` +
  `asyncio.gather` deixam as consultas concorrentes de forma natural; e a
  validação de entrada sai de graça via Pydantic (requisito 1 → resposta 422).
- **Provider atrás de uma interface (`UserProvider`):** a regra de negócio
  (`services.fetch_users`) depende de uma abstração, não de `httpx`. Trocar a
  API externa — ou usar um `FakeUserProvider` nos testes — não muda a regra.
- **Erros como vocabulário de domínio:** o provider traduz timeout/404/erros de
  rede para `UserNotFound`, `ProviderTimeout` e `ProviderUnavailable`. A regra
  só conhece essas exceções.
- **Isolamento de falha:** `asyncio.gather(..., return_exceptions=True)` + um
  `try/except` lógico por id garantem que uma falha vire um item em `failed`,
  sem abortar o lote (requisito 4).
- **Concorrência limitada:** um `asyncio.Semaphore` limita chamadas simultâneas
  ao provider (evita estourar o serviço externo).
- **Cliente HTTP único:** um `httpx.AsyncClient` no ciclo de vida da app
  reaproveita conexões.
- **Front com estados explícitos:** loading, erro, encontrados e falhados — sem
  tela ambígua.

## O que eu melhoraria com mais tempo

- **Retry com backoff exponencial + tratamento de 429** no provider.
- **Logging estruturado** (JSON) e métricas (contadores de sucesso/falha, latência).
- **Cache** (ex.: Redis) para IDs consultados com frequência.
- **Testes do provider HTTP** mockando a rede (ex.: `respx`) e um teste de
  ponta a ponta na rota via `TestClient`.
- **Docker Compose** para subir backend + frontend com um comando.
- **Distinguir os motivos da falha** no retorno (não achado × timeout × erro),
  hoje agrupados em `failed`.

## Utilizei IA?

**Sim.** Usei o Claude (Anthropic) como par de programação para acelerar o
scaffolding, revisar o desenho das camadas (isolamento do provider e
tratamento de erros) e redigir este README. Todas as decisões técnicas foram
revisadas e compreendidas por mim.

## "Se precisasse consultar milhares de usuários, o que você mudaria?"

O gargalo deixa de ser o código e passa a ser o serviço externo e a memória.
Mudanças:

1. **Concorrência limitada e ajustável** (já há um `Semaphore`) — nunca disparar
   milhares de chamadas de uma vez; calibrar o teto conforme o rate limit do provider.
2. **Consumo em streaming/lotes** em vez de `gather` de tudo de uma vez, para não
   segurar milhares de corrotinas e resultados na memória ao mesmo tempo.
3. **Retry com backoff + respeito ao 429** (`Retry-After`).
4. **Endpoint em lote no provider**, se existir, para trocar N requisições por poucas.
5. **Cache** dos usuários já buscados e **persistência** (ex.: PostgreSQL) dos resultados.
6. **Processamento assíncrono** para volumes muito grandes: enfileirar o job
   (ex.: Celery/RQ) e devolver um `job_id` que o front consulta — em vez de uma
   requisição HTTP síncrona de longa duração.
7. **Timeouts, pool de conexões e backpressure** bem definidos, com observabilidade
   (latência, taxa de erro, throughput).

## Bônus — LLM em produção (classificar cada usuário, JSON confiável)

Trataria a classificação como mais um passo do pipeline, depois de obter o usuário:

- **Saída estruturada forçada por schema:** usar *function/tool calling* ou
  `response_format` com JSON Schema (OpenAI/Anthropic/Gemini) para o modelo
  responder **exatamente** no formato esperado, com `temperature` baixa.
- **Validação com Pydantic** do JSON retornado; se não validar, **1 retry** com o
  erro no prompt e, persistindo a falha, marcar o usuário como
  `classification: "unknown"` em vez de quebrar a resposta.
- **Categorias como `enum`** no schema, evitando texto livre / alucinação de rótulos.
- **Concorrência limitada + backoff** para os limites de rate do provider de LLM,
  igual ao provider HTTP.
- **Cache por entrada** (mesmo usuário → mesma categoria) para reduzir custo e latência.
- Manter a chamada ao LLM **atrás de uma interface** (`Classifier`), como o
  `UserProvider`, para trocar de modelo/fornecedor sem tocar na regra.
